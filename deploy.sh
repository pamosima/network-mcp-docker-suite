#!/bin/bash
# Network MCP Docker Suite - Deployment Helper Script
# =============================================
# Supports deployment of multiple MCP servers:
# - Meraki MCP Server: Cisco Meraki cloud management
# - NetBox MCP Server: Network documentation and IPAM  
# - Catalyst Center MCP Server: Cisco Catalyst Center integration
# - IOS XE MCP Server: Direct device management via SSH
#
# Updated: 2025-10-14 - Added IOS XE MCP server support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Network MCP Docker Suite - Deployment Helper${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [PROFILE]"
    echo ""
    echo "Commands:"
    echo "  start     Start servers"
    echo "  stop      Stop servers"
    echo "  restart   Restart servers"
    echo "  status    Show status"
    echo "  logs      Show logs"
    echo "  build     Build images"
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
    echo "  $0 start all          # Start all servers"
    echo "  $0 start meraki       # Start only Meraki server"
    echo "  $0 start thousandeyes # Start only ThousandEyes server"
    echo "  $0 start ise          # Start only ISE server"
    echo "  $0 start ios-xe       # Start only IOS XE server"
    echo "  $0 start splunk       # Start only Splunk server"
    echo "  $0 start cisco        # Start Cisco-focused servers"
    echo "  $0 start security     # Start security-focused servers"
    echo "  $0 stop all           # Stop all servers"
    echo "  $0 logs thousandeyes  # Show ThousandEyes server logs"
    echo "  $0 logs ise           # Show ISE server logs"
    echo "  $0 logs ios-xe        # Show IOS XE server logs"
    echo "  $0 logs splunk        # Show Splunk server logs"
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

# Build service arguments
SERVICE_ARGS=$(build_service_args $PROFILE)

# Execute commands
case $COMMAND in
    "start")
        echo -e "${GREEN}Starting MCP servers with profile: $PROFILE${NC}"
        
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
        echo -e "${GREEN}Servers started successfully!${NC}"
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
