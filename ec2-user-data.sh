#!/bin/bash

###############################################################################
# EC2 User Data Script
# This script runs automatically when launching an EC2 instance
# Use this in the "User Data" field when creating an EC2 instance
###############################################################################

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting EC2 User Data Script..."
echo "Timestamp: $(date)"

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    htop \
    curl \
    wget \
    unzip

# Create ubuntu user home directory if not exists
cd /home/ubuntu

# Clone project (replace with your repository URL)
# Uncomment and modify the following line:
# git clone https://github.com/your-username/your-repo.git project-1

# OR download from S3 (if you've uploaded your project there)
# Uncomment and modify:
# aws s3 cp s3://your-bucket/project-1.zip .
# unzip project-1.zip

# For now, we'll assume the project is uploaded separately
# Create placeholder directory
mkdir -p /home/ubuntu/project-1
cd /home/ubuntu/project-1

# Create a simple placeholder requirements.txt if not exists
cat > requirements.txt << 'EOF'
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
matplotlib==3.7.2
seaborn==0.12.2
boto3==1.28.25
Flask==2.3.3
requests==2.31.0
EOF

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Set proper permissions
chown -R ubuntu:ubuntu /home/ubuntu/project-1

# Create a simple status file
cat > /home/ubuntu/ec2-setup-complete.txt << EOF
EC2 Setup Complete
Timestamp: $(date)
Public IP: $(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)
Region: $(curl -s http://169.254.169.254/latest/meta-data/placement/region)
EOF

echo "User Data Script Complete!"
echo "Check /var/log/user-data.log for details"
