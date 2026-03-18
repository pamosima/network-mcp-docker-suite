# GitLab MCP Server

A FastMCP server that provides GitLab API integration for AI-driven CI/CD operations and repository management. Enables AI assistants to trigger pipelines, monitor jobs, retrieve logs/artifacts, and update repository files for network automation workflows.

## Features

- **Pipeline Triggering**: Trigger CI/CD pipelines with controlled variables (e.g., Ansible dry-runs)
- **Manual Job Execution**: Play manual jobs after dry-run (apply, rollback)
- **Status Monitoring**: Check pipeline and job status in real-time
- **Log Retrieval**: Get job logs to analyze dry-run output
- **Artifact Download**: Download specific job artifacts (e.g., diff logs)
- **Repository File Management**: Read and update config files (Ansible vars, templates)
- **Project Discovery**: List accessible projects and recent pipelines

## Use Case

The primary use case is **AI-driven network configuration management**:

1. User says: "Set NTP server 10.0.0.1 for core-01 and run a dry-run"
2. AI uses `update_gitlab_repository_file` to update `host_vars/core-01/ntp.yml`
3. AI uses `trigger_gitlab_pipeline` with `DRY_RUN=true` and `TARGET_HOST=core-01`
4. AI uses `get_gitlab_pipeline_status` to monitor the pipeline
5. AI uses `get_gitlab_job_logs` to retrieve and summarize the dry-run diff

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GITLAB_URL` | GitLab instance URL | `https://gitlab.com` |
| `GITLAB_TOKEN` | Personal access token (api scope) | (required) |
| `GITLAB_DEFAULT_PROJECT_ID` | Default project ID | (optional) |
| `GITLAB_ALLOWED_VARIABLES` | Comma-separated allowed pipeline variable keys | See below |
| `GITLAB_ALLOWED_FILE_PATHS` | Comma-separated allowed file path prefixes | See below |
| `GITLAB_RATE_LIMIT_TRIGGER` | Max pipeline triggers per minute | `10` |
| `GITLAB_RATE_LIMIT_FILE_UPDATE` | Max file updates per minute | `30` |
| `MCP_HOST` | Server bind address | `0.0.0.0` |
| `MCP_PORT` | Server port | `8009` |

### Required GitLab Token Scopes

- `api` (full API access) - OR -
- `read_api` + `write_repository` (minimum for trigger and file updates)

## Tools

### `trigger_gitlab_pipeline`
Trigger a CI/CD pipeline in GitLab.

**Parameters:**
- `project_id` (string, optional): Project ID or path (uses default if not set)
- `ref` (string, optional): Branch or tag (default: "main")
- `variables` (object, optional): Pipeline variables (only allowlisted keys)

**Example:**
```
trigger_gitlab_pipeline(
  project_id="network/automation",
  ref="main",
  variables={"DRY_RUN": "true", "TARGET_HOST": "core-01"}
)
```

### `get_gitlab_pipeline_status`
Get the status of a GitLab pipeline.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `pipeline_id` (integer, required): Pipeline ID

### `get_gitlab_job_logs`
Get the logs of a GitLab job.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `job_id` (integer, required): Job ID

### `get_gitlab_job_artifact`
Get a specific artifact from a GitLab job.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `job_id` (integer, required): Job ID
- `artifact_path` (string, optional): Path to specific artifact file

### `list_gitlab_projects`
List GitLab projects accessible with the token.

**Parameters:**
- `search` (string, optional): Filter by name/path
- `per_page` (integer, optional): Results per page (default: 20)

### `list_gitlab_pipelines`
List recent pipelines for a project.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `per_page` (integer, optional): Results per page (default: 10)
- `status` (string, optional): Filter by status

### `play_gitlab_job`
Play (trigger) a manual job in a GitLab pipeline.

Use this to run manual jobs after a dry-run completes, such as:
- `apply_config`: Apply configuration changes after reviewing dry-run
- `rollback_apply`: Apply rollback after reviewing rollback_verify

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `job_id` (integer, required): Job ID to play (from `get_gitlab_pipeline_status` jobs list)

**Example workflow:**
```
1. trigger_gitlab_pipeline with DRY_RUN=true
2. get_gitlab_pipeline_status to find the manual apply_config job
3. Review the dry-run output with get_gitlab_job_logs
4. play_gitlab_job with the apply_config job ID to apply changes
```

### `get_gitlab_repository_file`
Read a file from the repository.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `file_path` (string, required): Path to file in repository
- `ref` (string, optional): Branch/tag/commit (default: "main")

### `update_gitlab_repository_file`
Create or update a file in the repository.

**Parameters:**
- `project_id` (string, optional): Project ID or path
- `file_path` (string, required): Path to file
- `content` (string, required): New file content
- `branch` (string, optional): Target branch (default: "main")
- `commit_message` (string, required): Commit message

## Security

### Allowlisted Pipeline Variables

Only these variables are accepted when triggering pipelines:

```
DRY_RUN, TARGET_HOST, TARGET_HOSTS, SITE_PIPELINE, SWITCH_PIPELINE,
PLAYBOOK, EXTRA_VARS, LIMIT, TAGS, SKIP_TAGS, VERBOSITY
```

Configure via `GITLAB_ALLOWED_VARIABLES` environment variable.

### Allowed File Paths

Repository file operations are restricted to these prefixes:

```
ansible/, host_vars/, group_vars/, configs/, templates/,
inventory/, playbooks/, roles/, vars/
```

Configure via `GITLAB_ALLOWED_FILE_PATHS` environment variable.

### Blocked File Patterns

These patterns are always blocked:
- `.gitlab-ci.yml` (CI config)
- `.env*` (environment files)
- `*secrets*` (secret files)
- `.git/`, `.ssh/` (git/ssh directories)
- `*.pem`, `*.key`, `id_rsa` (private keys)
- `Dockerfile`, `docker-compose*` (Docker configs)

### Rate Limiting

- Pipeline triggers: 10 per minute (configurable)
- File updates: 30 per minute (configurable)

## Example Prompts

**Trigger a dry-run:**
```
Trigger a dry-run pipeline for project network/automation with TARGET_HOST=core-01
```

**Check pipeline status:**
```
What's the status of pipeline 12345 in project network/automation?
```

**Get job logs:**
```
Show me the logs for job 67890 - I want to see the Ansible dry-run output
```

**Update config and dry-run:**
```
Update the NTP server to 10.0.0.1 for core-01 in the ansible host_vars,
then trigger a dry-run to show me the diff
```

**List recent pipelines:**
```
Show me the last 5 failed pipelines for project network/automation
```

## Integration with netops-stack

This server is designed for the **Orchestrator** workflow:

1. **Intent Layer**: AI updates intended config in Git via `update_gitlab_repository_file`
2. **Dry-Run**: AI triggers Ansible pipeline with `DRY_RUN=true`
3. **Review**: AI retrieves logs/artifacts to show config diff
4. **Apply**: User approves, AI uses `play_gitlab_job` to run the manual apply job

### Workflow Example

```
User: "Add VLAN 100 on sw11-1"

AI workflow:
1. update_gitlab_repository_file → ansible/configs/desired/sw11-1.txt
2. trigger_gitlab_pipeline → DRY_RUN=true, TARGET_HOST=sw11-1
3. get_gitlab_pipeline_status → find job IDs
4. get_gitlab_job_logs → show dry-run diff to user
5. [User approves]
6. play_gitlab_job → trigger apply_config job
```
