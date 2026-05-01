#!/bin/bash
# Network MCP Docker Suite - Deployment Helper Script
# =============================================
# Supports deployment of multiple MCP servers:
# - Meraki MCP Server: Cisco Meraki cloud management
# - NetBox MCP Server: Network documentation and IPAM  
# - Catalyst Center MCP Server: Cisco Catalyst Center integration
# - IOS XE MCP Server: Direct device management via SSH
# - ThousandEyes MCP Server: Network performance monitoring
# - ISE MCP Server: Identity and access control
# - Splunk MCP Server: Log analysis and SIEM
# - Prometheus MCP Server: Metrics queries (gnp-stack/netops-stack)
# - ClickHouse MCP Server: Syslog queries (gnp-stack/netops-stack)
# - GitLab MCP Server: CI/CD pipeline orchestration
# - NetOps MCP Gateway: single endpoint aggregating other MCP servers
#
# Features:
# - Enable/disable individual servers via .env file (ENABLE_*_MCP)
# - Flexible deployment profiles (all, cisco, monitoring, security, netops-stack, etc.)
# - Automatic filtering of disabled servers
#
# Updated: 2026-02-24 - Added Prometheus, ClickHouse, GitLab servers and netops-stack profile
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load .env file if it exists
if [ -f .env ]; then
    # Load .env file, handling inline comments
    while IFS= read -r line || [ -n "$line" ]; do
        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Remove inline comments and export
        line=$(echo "$line" | sed 's/#.*$//' | xargs)
        [[ -n "$line" ]] && export "$line"
    done < .env
    echo -e "${BLUE}✅ Loaded configuration from .env${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found — set ENABLE_*_MCP=true in .env for each server you want${NC}"
    echo -e "${YELLOW}   Copy .env.example to .env${NC}"
fi

# Function to check if a server is enabled
is_enabled() {
    local server=$1
    local var_name=""
    
    case $server in
        "meraki-mcp-servers")
            var_name="ENABLE_MERAKI_MCP"
            ;;
        "netbox-mcp-server")
            var_name="ENABLE_NETBOX_MCP"
            ;;
        "catc-mcp-server")
            var_name="ENABLE_CATC_MCP"
            ;;
        "ios-xe-mcp-server")
            var_name="ENABLE_IOS_XE_MCP"
            ;;
        "thousandeyes-mcp-server")
            var_name="ENABLE_THOUSANDEYES_MCP"
            ;;
        "ise-mcp-server")
            var_name="ENABLE_ISE_MCP"
            ;;
        "splunk-mcp-server")
            var_name="ENABLE_SPLUNK_MCP"
            ;;
        "prometheus-mcp-server")
            var_name="ENABLE_PROMETHEUS_MCP"
            ;;
        "clickhouse-mcp-server")
            var_name="ENABLE_CLICKHOUSE_MCP"
            ;;
        "gitlab-mcp-server")
            var_name="ENABLE_GITLAB_MCP"
            ;;
        "netops-mcp-gateway")
            var_name="ENABLE_NETOPS_MCP_GATEWAY"
            ;;
    esac
    
    if [ -z "$var_name" ]; then
        return 0
    fi
    local enabled=$(eval echo \$$var_name)
    if [[ "$enabled" =~ ^(true|True|TRUE|1|yes|Yes|YES)$ ]]; then
        return 0
    fi
    return 1
}

# Compose project file chain (optional local override).
setup_compose_file() {
    COMPOSE_FILE="docker-compose.yml"
    if [ -f docker-compose.override.yml ]; then
        COMPOSE_FILE="${COMPOSE_FILE}:docker-compose.override.yml"
    fi
    export COMPOSE_FILE
}

# Function to filter enabled services
filter_enabled_services() {
    local services=$1
    local enabled_services=""
    local disabled_services=""
    
    for service in $services; do
        if is_enabled $service; then
            enabled_services="$enabled_services $service"
        else
            disabled_services="$disabled_services $service"
        fi
    done
    
    # Show disabled services if any
    if [ -n "$disabled_services" ]; then
        echo -e "${YELLOW}ℹ️  Skipping disabled servers:$disabled_services${NC}" >&2
    fi
    
    echo $enabled_services
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Network MCP Docker Suite - Deployment Helper${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [PROFILE]"
    echo ""
    echo -e "${YELLOW}Note: Only servers with ENABLE_*_MCP=true are started, built, stopped, or logged${NC}"
    echo ""
    echo "Commands:"
    echo "  start     Start servers"
    echo "  stop      Stop servers"
    echo "  restart   Restart servers"
    echo "  status    Show status"
    echo "  logs      Show logs"
    echo "  build     Build images"
    echo "  cleanup   Stop and remove disabled servers"
    echo ""
    echo "Profiles:"
    echo "  all         All servers (all 11 MCP servers including NetOps MCP Gateway)"
    echo "  meraki      Meraki MCP server only"
    echo "  netbox      NetBox MCP server only"
    echo "  catc        Catalyst Center MCP server only"
    echo "  thousandeyes ThousandEyes MCP server only"
    echo "  ise         ISE MCP server only"
    echo "  ios-xe      IOS XE MCP server only"
    echo "  splunk      Splunk MCP server only"
    echo "  prometheus  Prometheus MCP server only"
    echo "  clickhouse  ClickHouse MCP server only"
    echo "  gitlab      GitLab MCP server only"
    echo "  netops-gateway  NetOps MCP Gateway only (aggregates other MCP servers)"
    echo "  cisco       Cisco-focused (Meraki + Catalyst Center + ThousandEyes + ISE + IOS XE)"
    echo "  network     Network management (Meraki + ThousandEyes + IOS XE)"
    echo "  security    Security-focused (Catalyst Center + ISE)"
    echo "  monitoring  Network monitoring (Meraki + Catalyst Center + ThousandEyes + Splunk)"
    echo "  docs        Documentation-focused (NetBox + Catalyst Center)"
    echo "  observability gnp-stack integration (Prometheus + ClickHouse + NetBox)"
    echo "  orchestration CI/CD automation (GitLab + NetBox + IOS XE)"
    echo "  netops-stack  netops-stack integration (ClickHouse + GitLab + IOS XE + NetBox + Prometheus)"
    echo ""
    echo "Examples:"
    echo "  $0 start all          # Start all enabled servers"
    echo "  $0 start meraki       # Start only Meraki server (if enabled)"
    echo "  $0 start cisco        # Start Cisco-focused servers (if enabled)"
    echo "  $0 start netops-stack # Starts MCP Servers for: ClickHouse, GitLab, IOS-XE, NetBox, Prometheus"
    echo "  $0 cleanup            # Stop and remove disabled servers"
    echo "  $0 stop all           # Stop enabled servers for this profile (see stop output)"
    echo "  $0 status all         # Show status of enabled servers"
    echo "  $0 logs gitlab        # Show GitLab server logs"
    echo ""
    echo "Workflow after disabling servers in .env:"
    echo "  1. Edit .env and set ENABLE_*_MCP=false"
    echo "  2. Run: $0 cleanup"
    echo "  3. Run: $0 start all"
    echo ""
}


# Function to build service arguments
build_service_args() {
    local profile=$1
    case $profile in
        "all")
            echo "meraki-mcp-servers netbox-mcp-server catc-mcp-server thousandeyes-mcp-server ise-mcp-server ios-xe-mcp-server splunk-mcp-server prometheus-mcp-server clickhouse-mcp-server gitlab-mcp-server netops-mcp-gateway"
            ;;
        "meraki")
            echo "meraki-mcp-servers"
            ;;
        "netbox")
            echo "netbox-mcp-server"
            ;;
        "catc"|"catalyst")
            echo "catc-mcp-server"
            ;;
        "thousandeyes"|"te")
            echo "thousandeyes-mcp-server"
            ;;
        "ise")
            echo "ise-mcp-server"
            ;;
        "ios-xe"|"iosxe")
            echo "ios-xe-mcp-server"
            ;;
        "splunk")
            echo "splunk-mcp-server"
            ;;
        "prometheus"|"prom")
            echo "prometheus-mcp-server"
            ;;
        "clickhouse"|"ch")
            echo "clickhouse-mcp-server"
            ;;
        "gitlab"|"gl")
            echo "gitlab-mcp-server"
            ;;
        "netops-gateway"|"suite-gateway"|"gateway")
            echo "netops-mcp-gateway"
            ;;
        "cisco")
            echo "meraki-mcp-servers catc-mcp-server thousandeyes-mcp-server ise-mcp-server ios-xe-mcp-server"
            ;;
        "network"|"networking")
            echo "meraki-mcp-servers thousandeyes-mcp-server ios-xe-mcp-server"
            ;;
        "security")
            echo "catc-mcp-server ise-mcp-server"
            ;;
        "management")
            echo "meraki-mcp-servers catc-mcp-server"
            ;;
        "docs"|"documentation")
            echo "netbox-mcp-server catc-mcp-server"
            ;;
        "monitoring")
            echo "meraki-mcp-servers catc-mcp-server thousandeyes-mcp-server splunk-mcp-server"
            ;;
        "observability"|"obs")
            echo "prometheus-mcp-server clickhouse-mcp-server netbox-mcp-server"
            ;;
        "orchestration"|"orch")
            echo "gitlab-mcp-server netbox-mcp-server ios-xe-mcp-server"
            ;;
        "netops-stack"|"netops")
            echo "clickhouse-mcp-server gitlab-mcp-server ios-xe-mcp-server netbox-mcp-server prometheus-mcp-server"
            ;;
        *)
            echo -e "${RED}Error: Unknown profile '$profile'${NC}"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Parse arguments
COMMAND=$1
PROFILE=${2:-"all"}

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

if [[ "$COMMAND" == "help" || "$COMMAND" == "-h" || "$COMMAND" == "--help" ]]; then
    show_usage
    exit 0
fi

# Build service arguments and filter for enabled services
SERVICE_ARGS_RAW=$(build_service_args $PROFILE)
SERVICE_ARGS=$(filter_enabled_services "$SERVICE_ARGS_RAW")

setup_compose_file
if [[ "$COMMAND" == "start" || "$COMMAND" == "build" ]]; then
    echo -e "${BLUE}ℹ️  COMPOSE_FILE=${COMPOSE_FILE}${NC}" >&2
fi

# Check if any services are enabled
if [ -z "$SERVICE_ARGS" ]; then
    echo -e "${RED}❌ Error: No enabled servers for profile '$PROFILE'${NC}"
    echo -e "${YELLOW}   Enable servers in .env file using ENABLE_*_MCP=true${NC}"
    exit 1
fi

# Execute commands
case $COMMAND in
    "start")
        echo -e "${GREEN}Starting MCP servers with profile: $PROFILE${NC}"
        
        # Count enabled servers
        SERVER_COUNT=$(echo $SERVICE_ARGS | wc -w | tr -d ' ')
        echo -e "${BLUE}📊 Starting $SERVER_COUNT enabled server(s)${NC}"
        
        # Special message for IOS XE server
        if [[ $SERVICE_ARGS == *"ios-xe-mcp-server"* ]]; then
            echo -e "${BLUE}🔐 Starting IOS XE MCP Server${NC}"
            echo -e "${YELLOW}   Environment-only credentials required (.env file)${NC}"
        fi
        
        docker-compose up -d $SERVICE_ARGS
        echo -e "${GREEN}✅ Servers started successfully!${NC}"
        echo -e "${YELLOW}Use '$0 status $PROFILE' to check status${NC}"
        
        # Additional info for IOS XE server
        if [[ $SERVICE_ARGS == *"ios-xe-mcp-server"* ]]; then
            echo -e "${BLUE}💡 IOS XE Server: No credential parameters needed - uses .env only${NC}"
        fi
        ;;
    "stop")
        echo -e "${YELLOW}Stopping MCP servers with profile: $PROFILE${NC}"
        docker-compose stop $SERVICE_ARGS
        echo -e "${GREEN}Servers stopped successfully!${NC}"
        echo -e "${BLUE}   Stopped only services enabled in .env for this profile. Full teardown: docker compose down${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}Restarting MCP servers with profile: $PROFILE${NC}"
        docker-compose restart $SERVICE_ARGS
        echo -e "${GREEN}Servers restarted successfully!${NC}"
        ;;
    "status")
        echo -e "${BLUE}Status for profile: $PROFILE${NC}"
        docker-compose ps $SERVICE_ARGS
        ;;
    "logs")
        echo -e "${BLUE}Logs for profile: $PROFILE (enabled services only)${NC}"
        docker-compose logs -f $SERVICE_ARGS
        ;;
    "build")
        echo -e "${YELLOW}Building images for profile: $PROFILE${NC}"
        docker-compose build $SERVICE_ARGS
        echo -e "${GREEN}Images built successfully!${NC}"
        ;;
    "cleanup")
        echo -e "${YELLOW}🧹 Cleaning up disabled servers...${NC}"
        
        ALL_SERVERS="meraki-mcp-servers netbox-mcp-server catc-mcp-server thousandeyes-mcp-server ise-mcp-server ios-xe-mcp-server splunk-mcp-server prometheus-mcp-server clickhouse-mcp-server gitlab-mcp-server netops-mcp-gateway"
        
        STOPPED_COUNT=0
        for service in $ALL_SERVERS; do
            if ! is_enabled $service; then
                if docker-compose ps -aq "$service" 2>/dev/null | grep -q .; then
                    echo -e "${BLUE}  Stopping and removing: $service${NC}"
                    docker-compose stop "$service" 2>/dev/null || true
                    docker-compose rm -f "$service" 2>/dev/null || true
                    STOPPED_COUNT=$((STOPPED_COUNT + 1))
                fi
            fi
        done
        
        if [ $STOPPED_COUNT -eq 0 ]; then
            echo -e "${GREEN}✅ No disabled servers are running${NC}"
        else
            echo -e "${GREEN}✅ Stopped and removed $STOPPED_COUNT disabled server(s)${NC}"
        fi
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
