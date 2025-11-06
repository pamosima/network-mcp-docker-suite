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
#
# Features:
# - Enable/disable individual servers via .env file (ENABLE_*_MCP)
# - Flexible deployment profiles (all, cisco, monitoring, security, etc.)
# - Automatic filtering of disabled servers
#
# Updated: 2025-11-06 - Added .env integration for enable/disable control

set -e

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
    echo -e "${YELLOW}⚠️  No .env file found - all servers will be attempted${NC}"
    echo -e "${YELLOW}   Copy .env.example to .env to configure which servers to enable${NC}"
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
    esac
    
    # If no .env file or variable not set, default to enabled
    if [ -z "$var_name" ]; then
        return 0
    fi
    
    # Get the value of the enable variable
    local enabled=$(eval echo \$$var_name)
    
    # Check if enabled (true, True, TRUE, 1, yes, Yes, YES)
    if [[ "$enabled" =~ ^(true|True|TRUE|1|yes|Yes|YES)$ ]]; then
        return 0
    else
        return 1
    fi
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
    echo -e "${YELLOW}Note: Only enabled servers in .env will start (ENABLE_*_MCP=true)${NC}"
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
    echo "  all       All servers (Meraki + NetBox + Catalyst Center + ThousandEyes + ISE + IOS XE)"
    echo "  meraki    Meraki MCP server only"
    echo "  netbox    NetBox MCP server only"
    echo "  catc      Catalyst Center MCP server only"
    echo "  thousandeyes ThousandEyes MCP server only"
    echo "  ise       ISE MCP server only"
    echo "  ios-xe    IOS XE MCP server only"
    echo "  cisco     Cisco-focused (Meraki + Catalyst Center + ThousandEyes + ISE + IOS XE)"
    echo "  network   Network management (Meraki + ThousandEyes + IOS XE)"
    echo "  security  Security-focused (Catalyst Center + ISE)"
    echo "  monitoring Network monitoring (Meraki + Catalyst Center + ThousandEyes)"
    echo "  docs      Documentation-focused (NetBox + Catalyst Center)"
    echo ""
    echo "Examples:"
    echo "  $0 start all          # Start all enabled servers"
    echo "  $0 start meraki       # Start only Meraki server (if enabled)"
    echo "  $0 start cisco        # Start Cisco-focused servers (if enabled)"
    echo "  $0 cleanup            # Stop and remove disabled servers"
    echo "  $0 stop all           # Stop all servers"
    echo "  $0 status all         # Show status of enabled servers"
    echo "  $0 logs meraki        # Show Meraki server logs"
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
            echo "meraki-mcp-servers netbox-mcp-server catc-mcp-server thousandeyes-mcp-server ise-mcp-server ios-xe-mcp-server splunk-mcp-server"
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

# Build service arguments and filter for enabled services
SERVICE_ARGS_RAW=$(build_service_args $PROFILE)
SERVICE_ARGS=$(filter_enabled_services "$SERVICE_ARGS_RAW")

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
        
        if [ "$PROFILE" = "all" ]; then
            docker-compose up -d
        else
            docker-compose up -d $SERVICE_ARGS
        fi
        echo -e "${GREEN}✅ Servers started successfully!${NC}"
        echo -e "${YELLOW}Use '$0 status $PROFILE' to check status${NC}"
        
        # Additional info for IOS XE server
        if [[ $SERVICE_ARGS == *"ios-xe-mcp-server"* ]]; then
            echo -e "${BLUE}💡 IOS XE Server: No credential parameters needed - uses .env only${NC}"
        fi
        ;;
    "stop")
        echo -e "${YELLOW}Stopping MCP servers with profile: $PROFILE${NC}"
        if [ "$PROFILE" = "all" ]; then
            docker-compose down
        else
            docker-compose stop $SERVICE_ARGS
        fi
        echo -e "${GREEN}Servers stopped successfully!${NC}"
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
        echo -e "${BLUE}Logs for profile: $PROFILE${NC}"
        if [ "$PROFILE" = "all" ]; then
            docker-compose logs -f
        else
            docker-compose logs -f $SERVICE_ARGS
        fi
        ;;
    "build")
        echo -e "${YELLOW}Building images for profile: $PROFILE${NC}"
        if [ "$PROFILE" = "all" ]; then
            docker-compose build
        else
            docker-compose build $SERVICE_ARGS
        fi
        echo -e "${GREEN}Images built successfully!${NC}"
        ;;
    "cleanup")
        echo -e "${YELLOW}🧹 Cleaning up disabled servers...${NC}"
        
        # Get all possible servers
        ALL_SERVERS="meraki-mcp-servers netbox-mcp-server catc-mcp-server thousandeyes-mcp-server ise-mcp-server ios-xe-mcp-server splunk-mcp-server"
        
        STOPPED_COUNT=0
        for service in $ALL_SERVERS; do
            if ! is_enabled $service; then
                # Check if container exists and is running
                if docker ps -a --format '{{.Names}}' | grep -q "^${service}$"; then
                    echo -e "${BLUE}  Stopping and removing: $service${NC}"
                    docker stop $service 2>/dev/null || true
                    docker rm $service 2>/dev/null || true
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
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
