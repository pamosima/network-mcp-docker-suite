"""
GitLab MCP Server
=================
A FastMCP server for GitLab API integration enabling AI-driven CI/CD operations.
Supports pipeline triggering, status monitoring, log retrieval, artifact download,
and repository file updates for network automation workflows.

Environment Variables:
    GITLAB_URL: GitLab instance URL (e.g., https://gitlab.com)
    GITLAB_TOKEN: Personal access token with api scope
    GITLAB_DEFAULT_PROJECT_ID: Default project ID (optional)
    GITLAB_ALLOWED_FILE_PATHS: Comma-separated allowed file path prefixes (optional)
    GITLAB_ALLOWED_VARIABLES: Comma-separated allowed pipeline variable keys (optional)
"""

import os
import re
import time
from typing import Any, Dict, Optional, List
from collections import defaultdict

import httpx
from fastmcp import FastMCP

# Configuration from environment
GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com").rstrip("/")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "")
GITLAB_DEFAULT_PROJECT_ID = os.getenv("GITLAB_DEFAULT_PROJECT_ID", "")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8009"))

# Security: Allowed pipeline variables
DEFAULT_ALLOWED_VARIABLES = [
    "DRY_RUN", "TARGET_HOST", "TARGET_HOSTS", "SITE_PIPELINE", "SWITCH_PIPELINE",
    "PLAYBOOK", "EXTRA_VARS", "LIMIT", "TAGS", "SKIP_TAGS", "VERBOSITY"
]
GITLAB_ALLOWED_VARIABLES = os.getenv(
    "GITLAB_ALLOWED_VARIABLES",
    ",".join(DEFAULT_ALLOWED_VARIABLES)
).split(",")

# Security: Allowed file path prefixes for repository file operations
DEFAULT_ALLOWED_FILE_PATHS = [
    "ansible/", "host_vars/", "group_vars/", "configs/", "templates/",
    "inventory/", "playbooks/", "roles/", "vars/"
]
GITLAB_ALLOWED_FILE_PATHS = os.getenv(
    "GITLAB_ALLOWED_FILE_PATHS",
    ",".join(DEFAULT_ALLOWED_FILE_PATHS)
).split(",")

# Security: Blocked file patterns
BLOCKED_FILE_PATTERNS = [
    r"\.gitlab-ci\.yml$",
    r"\.env",
    r"secrets?",
    r"\.git/",
    r"Dockerfile",
    r"docker-compose",
    r"\.ssh/",
    r"id_rsa",
    r"\.pem$",
    r"\.key$"
]

# Rate limiting: requests per minute
RATE_LIMIT_TRIGGER = int(os.getenv("GITLAB_RATE_LIMIT_TRIGGER", "10"))
RATE_LIMIT_FILE_UPDATE = int(os.getenv("GITLAB_RATE_LIMIT_FILE_UPDATE", "30"))
_rate_limit_tracker: Dict[str, List[float]] = defaultdict(list)

# Initialize FastMCP server
mcp = FastMCP(
    name="GitLab MCP Server",
    instructions="""GitLab MCP Server for CI/CD operations and repository management.

This server provides tools to:
- Trigger CI/CD pipelines (e.g., Ansible dry-runs)
- Monitor pipeline and job status
- Retrieve job logs and artifacts
- Update repository files (intended CLI config)

Use cases:
- "Trigger a dry-run pipeline for network config changes"
- "Check the status of pipeline 12345"
- "Show me the job logs for the Ansible dry-run"
- "Update the NTP config for core-01 and run a dry-run"

Security:
- Only allowlisted pipeline variables are accepted
- File updates restricted to allowed paths (ansible/, configs/, etc.)
- Rate limiting applied to prevent abuse
"""
)


def _check_rate_limit(operation: str, limit: int) -> Optional[str]:
    """Check if operation is within rate limit. Returns error message if exceeded."""
    now = time.time()
    window = 60  # 1 minute window
    
    # Clean old entries
    _rate_limit_tracker[operation] = [
        t for t in _rate_limit_tracker[operation] if now - t < window
    ]
    
    if len(_rate_limit_tracker[operation]) >= limit:
        return f"Rate limit exceeded for {operation}. Max {limit} requests per minute."
    
    _rate_limit_tracker[operation].append(now)
    return None


def _validate_file_path(file_path: str) -> Optional[str]:
    """Validate file path against allowlist and blocklist."""
    # Check blocked patterns
    for pattern in BLOCKED_FILE_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            return f"File path '{file_path}' matches blocked pattern"
    
    # Check allowed prefixes
    allowed = any(file_path.startswith(prefix) for prefix in GITLAB_ALLOWED_FILE_PATHS)
    if not allowed:
        return f"File path '{file_path}' not in allowed prefixes: {GITLAB_ALLOWED_FILE_PATHS}"
    
    return None


def _sanitize_commit_message(message: str, max_length: int = 500) -> str:
    """Sanitize commit message."""
    # Remove control characters except newlines
    message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', message)
    # Limit length
    if len(message) > max_length:
        message = message[:max_length] + "..."
    return message.strip()


def _filter_variables(variables: Dict[str, str]) -> Dict[str, str]:
    """Filter pipeline variables to only allowed keys."""
    return {
        k: v for k, v in variables.items()
        if k.upper() in [v.upper() for v in GITLAB_ALLOWED_VARIABLES]
    }


def _make_request(
    method: str,
    endpoint: str,
    params: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    raw_response: bool = False
) -> Dict[str, Any]:
    """Make a request to GitLab API."""
    if not GITLAB_TOKEN:
        return {"success": False, "error": "GITLAB_TOKEN not configured"}
    
    url = f"{GITLAB_URL}/api/v4/{endpoint}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )
            response.raise_for_status()
            
            if raw_response:
                return {"success": True, "data": response.text}
            
            if response.content:
                return {"success": True, "data": response.json()}
            return {"success": True, "data": None}
            
    except httpx.HTTPStatusError as e:
        error_detail = e.response.text[:500] if e.response.text else str(e)
        return {"success": False, "error": f"HTTP {e.response.status_code}: {error_detail}"}
    except httpx.RequestError as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _encode_path(path: str) -> str:
    """URL-encode a file path for GitLab API."""
    return path.replace("/", "%2F").replace(".", "%2E")


@mcp.tool()
def trigger_gitlab_pipeline(
    project_id: Optional[str] = None,
    ref: str = "main",
    variables: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Trigger a CI/CD pipeline in GitLab.
    
    Args:
        project_id: GitLab project ID or path (uses default if not specified)
        ref: Branch or tag to run pipeline on (default: main)
        variables: Pipeline variables (only allowlisted keys accepted)
    
    Returns:
        Pipeline ID, web URL, status, and message
    
    Security:
        Only these variables are allowed: DRY_RUN, TARGET_HOST, TARGET_HOSTS,
        SITE_PIPELINE, SWITCH_PIPELINE, PLAYBOOK, EXTRA_VARS, LIMIT, TAGS,
        SKIP_TAGS, VERBOSITY
    """
    # Rate limit check
    rate_error = _check_rate_limit("trigger", RATE_LIMIT_TRIGGER)
    if rate_error:
        return {"success": False, "error": rate_error}
    
    # Use default project if not specified
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required (no default configured)"}
    
    # Filter variables to allowed keys only
    filtered_vars = []
    if variables:
        allowed_vars = _filter_variables(variables)
        filtered_vars = [{"key": k, "value": v} for k, v in allowed_vars.items()]
        
        rejected = set(variables.keys()) - set(allowed_vars.keys())
        if rejected:
            return {
                "success": False,
                "error": f"Rejected variables (not in allowlist): {rejected}. "
                         f"Allowed: {GITLAB_ALLOWED_VARIABLES}"
            }
    
    # Trigger pipeline
    data = {"ref": ref}
    if filtered_vars:
        data["variables"] = filtered_vars
    
    result = _make_request("POST", f"projects/{project}/pipeline", json_data=data)
    
    if not result["success"]:
        return result
    
    pipeline = result["data"]
    return {
        "success": True,
        "pipeline_id": pipeline.get("id"),
        "web_url": pipeline.get("web_url"),
        "status": pipeline.get("status"),
        "ref": pipeline.get("ref"),
        "message": f"Pipeline {pipeline.get('id')} triggered on {ref}"
    }


@mcp.tool()
def get_gitlab_pipeline_status(
    project_id: Optional[str] = None,
    pipeline_id: int = 0
) -> Dict[str, Any]:
    """
    Get the status of a GitLab pipeline.
    
    Args:
        project_id: GitLab project ID or path
        pipeline_id: Pipeline ID to check
    
    Returns:
        Pipeline status, web URL, timestamps, and list of jobs
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not pipeline_id:
        return {"success": False, "error": "pipeline_id required"}
    
    # Get pipeline info
    result = _make_request("GET", f"projects/{project}/pipelines/{pipeline_id}")
    if not result["success"]:
        return result
    
    pipeline = result["data"]
    
    # Get jobs for this pipeline
    jobs_result = _make_request("GET", f"projects/{project}/pipelines/{pipeline_id}/jobs")
    jobs = []
    if jobs_result["success"] and jobs_result["data"]:
        jobs = [
            {
                "id": j.get("id"),
                "name": j.get("name"),
                "status": j.get("status"),
                "stage": j.get("stage"),
                "web_url": j.get("web_url")
            }
            for j in jobs_result["data"]
        ]
    
    return {
        "success": True,
        "pipeline_id": pipeline.get("id"),
        "status": pipeline.get("status"),
        "web_url": pipeline.get("web_url"),
        "ref": pipeline.get("ref"),
        "created_at": pipeline.get("created_at"),
        "started_at": pipeline.get("started_at"),
        "finished_at": pipeline.get("finished_at"),
        "duration": pipeline.get("duration"),
        "jobs": jobs
    }


@mcp.tool()
def get_gitlab_job_logs(
    project_id: Optional[str] = None,
    job_id: int = 0
) -> Dict[str, Any]:
    """
    Get the logs of a GitLab job.
    
    Args:
        project_id: GitLab project ID or path
        job_id: Job ID to get logs for
    
    Returns:
        Raw log text of the job
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not job_id:
        return {"success": False, "error": "job_id required"}
    
    result = _make_request("GET", f"projects/{project}/jobs/{job_id}/trace", raw_response=True)
    
    if not result["success"]:
        return result
    
    logs = result["data"]
    # Truncate very long logs
    max_length = 50000
    truncated = len(logs) > max_length
    if truncated:
        logs = logs[:max_length] + "\n\n... [TRUNCATED - log exceeds 50KB] ..."
    
    return {
        "success": True,
        "job_id": job_id,
        "logs": logs,
        "truncated": truncated
    }


@mcp.tool()
def get_gitlab_job_artifact(
    project_id: Optional[str] = None,
    job_id: int = 0,
    artifact_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get a specific artifact from a GitLab job.
    
    Args:
        project_id: GitLab project ID or path
        job_id: Job ID to get artifact from
        artifact_path: Path to specific artifact file (e.g., 'ansible/dry_run.log')
    
    Returns:
        Artifact content as text, or list of available artifacts
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not job_id:
        return {"success": False, "error": "job_id required"}
    
    if artifact_path:
        # Get specific artifact
        encoded_path = artifact_path.replace("/", "%2F")
        result = _make_request(
            "GET",
            f"projects/{project}/jobs/{job_id}/artifacts/{encoded_path}",
            raw_response=True
        )
        
        if not result["success"]:
            return result
        
        return {
            "success": True,
            "job_id": job_id,
            "artifact_path": artifact_path,
            "content": result["data"]
        }
    else:
        # List artifacts (get job details which includes artifacts info)
        result = _make_request("GET", f"projects/{project}/jobs/{job_id}")
        
        if not result["success"]:
            return result
        
        job = result["data"]
        artifacts = job.get("artifacts", [])
        
        return {
            "success": True,
            "job_id": job_id,
            "artifacts": artifacts,
            "artifacts_file": job.get("artifacts_file"),
            "message": "Specify artifact_path to download a specific artifact"
        }


@mcp.tool()
def list_gitlab_projects(
    search: Optional[str] = None,
    per_page: int = 20
) -> Dict[str, Any]:
    """
    List GitLab projects accessible with the configured token.
    
    Args:
        search: Filter projects by name/path
        per_page: Number of results (default: 20, max: 100)
    
    Returns:
        List of projects with ID, path, and web URL
    """
    params = {
        "per_page": min(per_page, 100),
        "order_by": "last_activity_at",
        "sort": "desc"
    }
    if search:
        params["search"] = search
    
    result = _make_request("GET", "projects", params=params)
    
    if not result["success"]:
        return result
    
    projects = [
        {
            "id": p.get("id"),
            "path_with_namespace": p.get("path_with_namespace"),
            "name": p.get("name"),
            "web_url": p.get("web_url"),
            "default_branch": p.get("default_branch")
        }
        for p in result["data"]
    ]
    
    return {
        "success": True,
        "count": len(projects),
        "projects": projects
    }


@mcp.tool()
def list_gitlab_pipelines(
    project_id: Optional[str] = None,
    per_page: int = 10,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """
    List recent pipelines for a GitLab project.
    
    Args:
        project_id: GitLab project ID or path
        per_page: Number of results (default: 10)
        status: Filter by status (pending, running, success, failed, canceled)
    
    Returns:
        List of recent pipelines
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    
    params = {"per_page": min(per_page, 100)}
    if status:
        params["status"] = status
    
    result = _make_request("GET", f"projects/{project}/pipelines", params=params)
    
    if not result["success"]:
        return result
    
    pipelines = [
        {
            "id": p.get("id"),
            "status": p.get("status"),
            "ref": p.get("ref"),
            "web_url": p.get("web_url"),
            "created_at": p.get("created_at"),
            "source": p.get("source")
        }
        for p in result["data"]
    ]
    
    return {
        "success": True,
        "count": len(pipelines),
        "pipelines": pipelines
    }


@mcp.tool()
def play_gitlab_job(
    project_id: Optional[str] = None,
    job_id: int = 0
) -> Dict[str, Any]:
    """
    Play (trigger) a manual job in a GitLab pipeline.
    
    Use this to run manual jobs after a dry-run completes, such as:
    - apply_config: Apply configuration changes after reviewing dry-run
    - rollback_apply: Apply rollback after reviewing rollback_verify
    
    Args:
        project_id: GitLab project ID or path (uses default if not specified)
        job_id: Job ID to play (from get_gitlab_pipeline_status jobs list)
    
    Returns:
        Job status and web URL after triggering
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not job_id:
        return {"success": False, "error": "job_id required"}
    
    result = _make_request("POST", f"projects/{project}/jobs/{job_id}/play")
    
    if not result["success"]:
        return result
    
    job = result["data"]
    return {
        "success": True,
        "job_id": job.get("id"),
        "name": job.get("name"),
        "status": job.get("status"),
        "web_url": job.get("web_url"),
        "pipeline_id": job.get("pipeline", {}).get("id") if job.get("pipeline") else None,
        "message": f"Job '{job.get('name')}' (ID: {job.get('id')}) triggered successfully"
    }


@mcp.tool()
def get_gitlab_repository_file(
    project_id: Optional[str] = None,
    file_path: str = "",
    ref: str = "main"
) -> Dict[str, Any]:
    """
    Get the content of a file from a GitLab repository.
    
    Args:
        project_id: GitLab project ID or path
        file_path: Path to the file in the repository
        ref: Branch, tag, or commit (default: main)
    
    Returns:
        File content and metadata
    
    Security:
        Only files in allowed paths can be read (ansible/, configs/, etc.)
    """
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not file_path:
        return {"success": False, "error": "file_path required"}
    
    # Validate file path
    path_error = _validate_file_path(file_path)
    if path_error:
        return {"success": False, "error": path_error}
    
    encoded_path = _encode_path(file_path)
    result = _make_request(
        "GET",
        f"projects/{project}/repository/files/{encoded_path}",
        params={"ref": ref}
    )
    
    if not result["success"]:
        return result
    
    file_data = result["data"]
    
    # Decode content
    import base64
    content = file_data.get("content", "")
    encoding = file_data.get("encoding", "base64")
    
    if encoding == "base64":
        try:
            content = base64.b64decode(content).decode("utf-8")
        except Exception:
            content = "[Binary content - cannot decode as text]"
    
    return {
        "success": True,
        "file_path": file_path,
        "ref": ref,
        "content": content,
        "last_commit_id": file_data.get("last_commit_id"),
        "size": file_data.get("size")
    }


@mcp.tool()
def update_gitlab_repository_file(
    project_id: Optional[str] = None,
    file_path: str = "",
    content: str = "",
    branch: str = "main",
    commit_message: str = ""
) -> Dict[str, Any]:
    """
    Create or update a file in a GitLab repository.
    
    Args:
        project_id: GitLab project ID or path
        file_path: Path to the file (e.g., 'ansible/host_vars/core-01/ntp.yml')
        content: New file content (UTF-8)
        branch: Branch to commit to (default: main)
        commit_message: Commit message (required)
    
    Returns:
        File path, branch, commit ID, and web URL
    
    Security:
        Only files in allowed paths can be updated (ansible/, configs/, etc.)
        Rate limited to prevent abuse
    """
    # Rate limit check
    rate_error = _check_rate_limit("file_update", RATE_LIMIT_FILE_UPDATE)
    if rate_error:
        return {"success": False, "error": rate_error}
    
    project = project_id or GITLAB_DEFAULT_PROJECT_ID
    if not project:
        return {"success": False, "error": "project_id required"}
    if not file_path:
        return {"success": False, "error": "file_path required"}
    if not content:
        return {"success": False, "error": "content required"}
    if not commit_message:
        return {"success": False, "error": "commit_message required"}
    
    # Validate file path
    path_error = _validate_file_path(file_path)
    if path_error:
        return {"success": False, "error": path_error}
    
    # Sanitize commit message
    commit_message = _sanitize_commit_message(commit_message)
    
    encoded_path = _encode_path(file_path)
    
    # Check if file exists
    check_result = _make_request(
        "GET",
        f"projects/{project}/repository/files/{encoded_path}",
        params={"ref": branch}
    )
    
    file_exists = check_result["success"]
    
    # Prepare data
    data = {
        "branch": branch,
        "content": content,
        "commit_message": commit_message
    }
    
    if file_exists:
        # Update existing file
        method = "PUT"
    else:
        # Create new file
        method = "POST"
    
    result = _make_request(
        method,
        f"projects/{project}/repository/files/{encoded_path}",
        json_data=data
    )
    
    if not result["success"]:
        return result
    
    file_data = result["data"]
    
    # Build web URL to the file
    web_url = f"{GITLAB_URL}/{project}/-/blob/{branch}/{file_path}"
    
    return {
        "success": True,
        "file_path": file_path,
        "branch": branch,
        "commit_id": file_data.get("commit_id") if file_data else None,
        "web_url": web_url,
        "action": "updated" if file_exists else "created",
        "message": f"File {'updated' if file_exists else 'created'} successfully"
    }


if __name__ == "__main__":
    print(f"🚀 Starting GitLab MCP Server")
    print(f"🦊 GitLab URL: {GITLAB_URL}")
    print(f"🔌 Listening on: {MCP_HOST}:{MCP_PORT}")
    print(f"")
    print(f"📋 Available tools:")
    print(f"   - trigger_gitlab_pipeline: Trigger CI/CD pipelines")
    print(f"   - get_gitlab_pipeline_status: Check pipeline status")
    print(f"   - get_gitlab_job_logs: Get job logs")
    print(f"   - get_gitlab_job_artifact: Download job artifacts")
    print(f"   - play_gitlab_job: Play manual jobs (apply, rollback)")
    print(f"   - list_gitlab_projects: List accessible projects")
    print(f"   - list_gitlab_pipelines: List recent pipelines")
    print(f"   - get_gitlab_repository_file: Read repository files")
    print(f"   - update_gitlab_repository_file: Update repository files")
    print(f"")
    print(f"🔒 Security:")
    print(f"   Allowed variables: {GITLAB_ALLOWED_VARIABLES}")
    print(f"   Allowed file paths: {GITLAB_ALLOWED_FILE_PATHS}")
    
    mcp.run(transport="streamable-http", host=MCP_HOST, port=MCP_PORT)
