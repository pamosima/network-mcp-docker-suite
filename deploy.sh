#!/bin/bash
# DevNet MCP Servers - Deployment Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}DevNet MCP Servers - Deployment Helper${NC}"
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
    echo "  all       All servers (Meraki + NetBox + Catalyst Center)"
    echo "  meraki    Meraki MCP server only"
    echo "  netbox    NetBox MCP server only"
    echo "  catc      Catalyst Center MCP server only"
    echo "  management Network management (Meraki + Catalyst Center)"
    echo "  docs      Documentation-focused (NetBox + Catalyst Center)"
    echo ""
    echo "Examples:"
    echo "  $0 start all          # Start all servers"
    echo "  $0 start meraki       # Start only Meraki server"
    echo "  $0 stop all           # Stop all servers"
    echo "  $0 logs meraki        # Show Meraki server logs"
    echo ""
}

# Function to build profile arguments
build_profile_args() {
    local profile=$1
    case $profile in
        "all")
            echo "--profile all"
            ;;
        "meraki")
            echo "--profile meraki"
            ;;
        "netbox")
            echo "--profile netbox"
            ;;
        "catc"|"catalyst")
            echo "--profile catc"
            ;;
        "management")
            echo "--profile meraki --profile catc"
            ;;
        "docs"|"documentation")
            echo "--profile netbox --profile catc"
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

# Build profile arguments
PROFILE_ARGS=$(build_profile_args $PROFILE)

# Execute commands
case $COMMAND in
    "start")
        echo -e "${GREEN}Starting MCP servers with profile: $PROFILE${NC}"
        docker-compose $PROFILE_ARGS up -d
        echo -e "${GREEN}Servers started successfully!${NC}"
        echo -e "${YELLOW}Use '$0 status $PROFILE' to check status${NC}"
        ;;
    "stop")
        echo -e "${YELLOW}Stopping MCP servers with profile: $PROFILE${NC}"
        docker-compose $PROFILE_ARGS down
        echo -e "${GREEN}Servers stopped successfully!${NC}"
        ;;
    "restart")
        echo -e "${YELLOW}Restarting MCP servers with profile: $PROFILE${NC}"
        docker-compose $PROFILE_ARGS restart
        echo -e "${GREEN}Servers restarted successfully!${NC}"
        ;;
    "status")
        echo -e "${BLUE}Status for profile: $PROFILE${NC}"
        docker-compose ps
        ;;
    "logs")
        echo -e "${BLUE}Logs for profile: $PROFILE${NC}"
        docker-compose logs -f
        ;;
    "build")
        echo -e "${YELLOW}Building images for profile: $PROFILE${NC}"
        docker-compose $PROFILE_ARGS build
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
