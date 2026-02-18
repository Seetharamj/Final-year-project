#!/bin/bash

###############################################################################
# EC2 Initial Setup Script
# Run this script once on a fresh EC2 instance to setup the environment
###############################################################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}EC2 Setup for Disaster Recovery System${NC}"
echo -e "${GREEN}========================================${NC}"

# Update system
echo -e "${YELLOW}[1/7] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

# Install Python
echo -e "${YELLOW}[2/7] Installing Python 3.9+...${NC}"
sudo apt install -y python3 python3-pip python3-venv
echo -e "${GREEN}✓ Python installed: $(python3 --version)${NC}"

# Install Git
echo -e "${YELLOW}[3/7] Installing Git...${NC}"
sudo apt install -y git
echo -e "${GREEN}✓ Git installed: $(git --version)${NC}"

# Install additional tools
echo -e "${YELLOW}[4/7] Installing additional tools...${NC}"
sudo apt install -y htop curl wget unzip
echo -e "${GREEN}✓ Additional tools installed${NC}"

# Setup project directory
echo -e "${YELLOW}[5/7] Setting up project directory...${NC}"
cd ~

# If project doesn't exist, you'll need to upload it
if [ ! -d "project-1" ]; then
    echo -e "${YELLOW}Project directory not found.${NC}"
    echo -e "${YELLOW}Please upload your project using:${NC}"
    echo -e "${YELLOW}  scp -i your-key.pem -r /path/to/project-1 ubuntu@YOUR-EC2-IP:~/${NC}"
    echo -e "${YELLOW}Or clone from Git:${NC}"
    echo -e "${YELLOW}  git clone <your-repo-url> project-1${NC}"
else
    echo -e "${GREEN}✓ Project directory found${NC}"
fi

# Setup Python virtual environment
if [ -d "project-1" ]; then
    echo -e "${YELLOW}[6/7] Setting up Python virtual environment...${NC}"
    cd ~/project-1
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate and install dependencies
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ requirements.txt not found${NC}"
    fi
    
    # Make startup script executable
    if [ -f "start-ec2.sh" ]; then
        chmod +x start-ec2.sh
        echo -e "${GREEN}✓ Startup script is executable${NC}"
    fi
    
    # Create logs directory
    mkdir -p logs
    echo -e "${GREEN}✓ Logs directory created${NC}"
fi

# Setup systemd service (optional)
echo -e "${YELLOW}[7/7] Setting up systemd service...${NC}"
if [ -f "~/project-1/disaster-recovery.service" ]; then
    read -p "Do you want to setup systemd service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo cp ~/project-1/disaster-recovery.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable disaster-recovery
        echo -e "${GREEN}✓ Systemd service configured${NC}"
        echo -e "${YELLOW}  Start with: sudo systemctl start disaster-recovery${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Service file not found, skipping${NC}"
fi

# Display summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo -e "1. Navigate to project: ${GREEN}cd ~/project-1${NC}"
echo -e "2. Start the system:    ${GREEN}./start-ec2.sh${NC}"
echo -e "3. Access dashboard:    ${GREEN}http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080${NC}"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo -e "  View logs:     ${GREEN}tail -f ~/project-1/logs/*.log${NC}"
echo -e "  Stop services: ${GREEN}pkill -f python3${NC}"
echo -e "  Check status:  ${GREEN}ps aux | grep python${NC}"
echo ""
echo -e "${GREEN}✓ All done!${NC}"
