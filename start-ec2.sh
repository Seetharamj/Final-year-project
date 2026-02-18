#!/bin/bash

###############################################################################
# EC2 Startup Script for AI-Driven Disaster Recovery System
# This script starts all components of the system on an EC2 instance
###############################################################################

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Starting Disaster Recovery System${NC}"
echo -e "${GREEN}========================================${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a process is running
check_process() {
    if pgrep -f "$1" > /dev/null; then
        echo -e "${GREEN}✓${NC} $2 is running"
        return 0
    else
        echo -e "${RED}✗${NC} $2 is not running"
        return 1
    fi
}

# Function to stop existing processes
stop_services() {
    echo -e "${YELLOW}Stopping existing services...${NC}"
    pkill -f "detector.py" 2>/dev/null
    pkill -f "predictor.py" 2>/dev/null
    pkill -f "http.server 8080" 2>/dev/null
    sleep 2
    echo -e "${GREEN}✓ Stopped existing services${NC}"
}

# Stop any existing services
stop_services

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment created and activated${NC}"
fi

# Start Anomaly Detection Model
echo -e "${YELLOW}Starting Anomaly Detection Model...${NC}"
if [ -f "ai-models/anomaly-detection/isolation-forest/detector.py" ]; then
    nohup python3 ai-models/anomaly-detection/isolation-forest/detector.py > logs/anomaly-detector.log 2>&1 &
    sleep 2
    if check_process "detector.py" "Anomaly Detection Model"; then
        echo -e "${GREEN}  Log: logs/anomaly-detector.log${NC}"
    fi
else
    echo -e "${YELLOW}  Skipping - detector.py not found${NC}"
fi

# Start Degradation Predictor
echo -e "${YELLOW}Starting Service Degradation Predictor...${NC}"
if [ -f "ai-models/prediction/degradation-predictor/predictor.py" ]; then
    nohup python3 ai-models/prediction/degradation-predictor/predictor.py > logs/degradation-predictor.log 2>&1 &
    sleep 2
    if check_process "predictor.py" "Degradation Predictor"; then
        echo -e "${GREEN}  Log: logs/degradation-predictor.log${NC}"
    fi
else
    echo -e "${YELLOW}  Skipping - predictor.py not found${NC}"
fi

# Start Dashboard
echo -e "${YELLOW}Starting Dashboard...${NC}"
if [ -d "dashboard/frontend" ]; then
    cd dashboard/frontend
    nohup python3 -m http.server 8080 > ../../logs/dashboard.log 2>&1 &
    cd "$SCRIPT_DIR"
    sleep 2
    if check_process "http.server 8080" "Dashboard"; then
        echo -e "${GREEN}  Log: logs/dashboard.log${NC}"
    fi
else
    echo -e "${RED}  Error - dashboard/frontend directory not found${NC}"
fi

# Get public IP (works on EC2)
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}System Status${NC}"
echo -e "${GREEN}========================================${NC}"

# Try to get EC2 public IP
PUBLIC_IP=$(curl -s --connect-timeout 2 http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
if [ -z "$PUBLIC_IP" ]; then
    # If not on EC2, use localhost
    PUBLIC_IP="localhost"
fi

echo -e "${GREEN}Dashboard URL:${NC} http://${PUBLIC_IP}:8080"
echo ""
echo -e "${YELLOW}Service Status:${NC}"
check_process "detector.py" "Anomaly Detection"
check_process "predictor.py" "Degradation Predictor"
check_process "http.server 8080" "Dashboard"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Useful Commands:${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "View logs:           ${YELLOW}tail -f logs/*.log${NC}"
echo -e "Stop all services:   ${YELLOW}pkill -f python3${NC}"
echo -e "Restart services:    ${YELLOW}./start-ec2.sh${NC}"
echo -e "Check processes:     ${YELLOW}ps aux | grep python${NC}"
echo ""
echo -e "${GREEN}✓ Startup complete!${NC}"
