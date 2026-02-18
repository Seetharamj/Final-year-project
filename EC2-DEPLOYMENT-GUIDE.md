# Running the Disaster Recovery System on EC2 Instance

## 🎯 Overview

This guide will help you deploy and run the AI-Driven Cloud-Based Disaster Recovery System on an AWS EC2 instance across multiple regions.

---

## 📋 Prerequisites

### 1. AWS Account Requirements
- Active AWS account with administrative access
- AWS CLI configured on your local machine
- SSH key pair for EC2 access
- Budget: ~$50-200/month for multi-region setup

### 2. Local Tools (for deployment)
```powershell
# Verify these are installed on your local machine:
aws --version        # AWS CLI v2
terraform --version  # Terraform >= 1.5.0
```

---

## 🚀 Deployment Options

### **Option A: Single EC2 Instance (Quick Start)**
Run everything on one EC2 instance in a single region.
- **Best for:** Testing, demos, development
- **Cost:** ~$10-20/month
- **Setup Time:** 15-30 minutes

### **Option B: Multi-Region EC2 Deployment (Production)**
Deploy EC2 instances across multiple regions with load balancing.
- **Best for:** Production, academic presentation
- **Cost:** ~$50-200/month
- **Setup Time:** 1-2 hours

---

## 🎬 Option A: Single EC2 Instance Deployment

### Step 1: Launch EC2 Instance

```powershell
# Navigate to terraform directory
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\infrastructure\terraform

# Initialize Terraform
terraform init

# Deploy infrastructure
terraform apply
```

**Alternatively, use AWS Console:**

1. Go to AWS Console → EC2 → Launch Instance
2. **Name:** disaster-recovery-dashboard
3. **AMI:** Ubuntu Server 22.04 LTS (Free Tier eligible)
4. **Instance Type:** t2.medium (recommended) or t2.micro (minimal)
5. **Key Pair:** Create or select existing key pair
6. **Security Group:** Configure as follows:
   - SSH (22) - Your IP only
   - HTTP (80) - Anywhere (0.0.0.0/0)
   - Custom TCP (8080) - Anywhere (0.0.0.0/0)
   - Custom TCP (5000) - Anywhere (0.0.0.0/0)
7. **Storage:** 20 GB gp3
8. Click **Launch Instance**

### Step 2: Connect to EC2 Instance

```powershell
# Get your instance public IP from AWS Console
# Example: ec2-xx-xx-xx-xx.compute-1.amazonaws.com

# Connect via SSH
ssh -i "your-key-pair.pem" ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

### Step 3: Install Dependencies on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install Node.js (if needed for dashboard)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Verify installations
python3 --version
pip3 --version
git --version
```

### Step 4: Clone Project to EC2

```bash
# Clone your project (if using Git)
git clone <your-repository-url>
cd project-1

# OR upload files using SCP from local machine:
# On your local Windows machine:
# scp -i "your-key-pair.pem" -r c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1 ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com:~/
```

### Step 5: Setup Python Environment on EC2

```bash
# Navigate to project directory
cd ~/project-1

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Run the System on EC2

**Option 1: Run Dashboard Only**
```bash
# Navigate to dashboard
cd ~/project-1/dashboard/frontend

# Start HTTP server
python3 -m http.server 8080 &

# Access at: http://YOUR-EC2-PUBLIC-IP:8080
```

**Option 2: Run Full System (AI Models + Dashboard)**

Create a startup script:

```bash
# Create startup script
cat > ~/project-1/start-ec2.sh << 'EOF'
#!/bin/bash

# Navigate to project
cd ~/project-1

# Activate virtual environment
source venv/bin/activate

# Start Anomaly Detection Model (background)
echo "Starting Anomaly Detection Model..."
nohup python3 ai-models/anomaly-detection/isolation-forest/detector.py > logs/anomaly-detector.log 2>&1 &

# Start Degradation Predictor (background)
echo "Starting Degradation Predictor..."
nohup python3 ai-models/prediction/degradation-predictor/predictor.py > logs/predictor.log 2>&1 &

# Start Dashboard (background)
echo "Starting Dashboard..."
cd dashboard/frontend
nohup python3 -m http.server 8080 > ../../logs/dashboard.log 2>&1 &

echo "All services started!"
echo "Dashboard: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8080"
EOF

# Make executable
chmod +x ~/project-1/start-ec2.sh

# Create logs directory
mkdir -p ~/project-1/logs

# Run the startup script
./start-ec2.sh
```

### Step 7: Access the Dashboard

```
Open browser to: http://YOUR-EC2-PUBLIC-IP:8080
```

### Step 8: Keep Services Running (Optional)

**Use systemd to run as a service:**

```bash
# Create systemd service file
sudo nano /etc/systemd/system/disaster-recovery.service
```

Add this content:
```ini
[Unit]
Description=Disaster Recovery System
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/project-1
ExecStart=/home/ubuntu/project-1/start-ec2.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable disaster-recovery
sudo systemctl start disaster-recovery
sudo systemctl status disaster-recovery
```

---

## 🌍 Option B: Multi-Region EC2 Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Region Setup                        │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ us-east-1    │  │ us-west-2    │  │ eu-west-1    │     │
│  │ (Primary)    │  │ (Secondary)  │  │ (DR Site)    │     │
│  │              │  │              │  │              │     │
│  │ EC2 Instance │  │ EC2 Instance │  │ EC2 Instance │     │
│  │ Dashboard    │  │ Dashboard    │  │ Dashboard    │     │
│  │ AI Models    │  │ AI Models    │  │ AI Models    │     │
│  │              │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ▲                 ▲                 ▲              │
│         └─────────────────┴─────────────────┘              │
│                  Load Balancer                             │
└─────────────────────────────────────────────────────────────┘
```

### Step 1: Deploy Infrastructure with Terraform

```powershell
# On your local machine
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\infrastructure\terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Deploy to all regions
terraform apply
```

This creates:
- ✅ VPCs in 3 regions
- ✅ EC2 instances in each region
- ✅ S3 buckets with cross-region replication
- ✅ CloudWatch monitoring
- ✅ Load balancers

### Step 2: Configure Each EC2 Instance

**For each region (us-east-1, us-west-2, eu-west-1):**

```bash
# SSH into each instance
ssh -i "your-key-pair.pem" ubuntu@<instance-public-ip>

# Run setup script
curl -o setup.sh https://raw.githubusercontent.com/your-repo/setup-ec2.sh
chmod +x setup.sh
./setup.sh
```

### Step 3: Setup Auto-Deployment Script

Create `setup-ec2.sh` in your project:

```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Clone project
cd ~
git clone <your-repo-url> project-1
cd project-1

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

# Start services
nohup python3 ai-models/anomaly-detection/isolation-forest/detector.py > logs/anomaly.log 2>&1 &
nohup python3 ai-models/prediction/degradation-predictor/predictor.py > logs/predictor.log 2>&1 &
cd dashboard/frontend && nohup python3 -m http.server 8080 > ../../logs/dashboard.log 2>&1 &

echo "Setup complete! Dashboard running on port 8080"
```

### Step 4: Configure Load Balancer

```bash
# Get all EC2 instance IPs
terraform output ec2_instances

# Configure Route53 or Application Load Balancer
# to distribute traffic across regions
```

---

## 🧪 Testing the Deployment

### 1. Verify Services are Running

```bash
# Check running processes
ps aux | grep python

# Check logs
tail -f ~/project-1/logs/anomaly.log
tail -f ~/project-1/logs/predictor.log
tail -f ~/project-1/logs/dashboard.log
```

### 2. Test Dashboard Access

```bash
# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Test locally on EC2
curl http://localhost:8080

# Test from browser
# http://YOUR-EC2-PUBLIC-IP:8080
```

### 3. Run Disaster Simulation

```bash
cd ~/project-1
source venv/bin/activate
python3 disaster-simulator/runner.py
```

---

## 🔒 Security Best Practices

### 1. Update Security Group Rules

```bash
# Only allow your IP for SSH
# Use HTTPS (443) instead of HTTP (80)
# Restrict port 8080 to specific IPs if needed
```

### 2. Setup SSL/TLS (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### 3. Enable CloudWatch Monitoring

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure monitoring
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config -m ec2 -s
```

---

## 📊 Monitoring and Logs

### View Real-time Logs

```bash
# Dashboard logs
tail -f ~/project-1/logs/dashboard.log

# AI Model logs
tail -f ~/project-1/logs/anomaly.log
tail -f ~/project-1/logs/predictor.log

# System logs
sudo journalctl -u disaster-recovery -f
```

### Monitor Resource Usage

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Network usage
sudo iftop
```

---

## 🛠️ Troubleshooting

### Issue: Cannot connect to EC2

**Solution:**
```bash
# Check security group allows your IP
# Verify instance is running
aws ec2 describe-instances --instance-ids i-xxxxx

# Check SSH key permissions
chmod 400 your-key-pair.pem
```

### Issue: Services not starting

**Solution:**
```bash
# Check Python version
python3 --version

# Verify virtual environment
source venv/bin/activate
which python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Port 8080 already in use

**Solution:**
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Or use different port
python3 -m http.server 8081
```

### Issue: Dashboard shows no data

**Solution:**
```bash
# Verify AI models are running
ps aux | grep python

# Check model logs for errors
tail -f ~/project-1/logs/anomaly.log

# Restart services
./start-ec2.sh
```

---

## 💰 Cost Optimization

### 1. Use Spot Instances
- Save up to 90% on EC2 costs
- Good for development/testing

### 2. Stop Instances When Not Needed
```bash
# Stop instance
aws ec2 stop-instances --instance-ids i-xxxxx

# Start instance
aws ec2 start-instances --instance-ids i-xxxxx
```

### 3. Use Auto Scaling
- Scale down during off-hours
- Scale up during peak usage

### 4. Monitor Costs
```bash
# Check current costs
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## 🧹 Cleanup

### Stop Services

```bash
# Stop all Python processes
pkill -f python3

# Or stop systemd service
sudo systemctl stop disaster-recovery
```

### Terminate EC2 Instance

```powershell
# From local machine
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\infrastructure\terraform

# Destroy all resources
terraform destroy
```

**Or via AWS Console:**
1. Go to EC2 → Instances
2. Select instance → Actions → Terminate

---

## 📈 Next Steps

1. **Setup Domain Name**
   - Register domain
   - Point to EC2 elastic IP
   - Configure SSL certificate

2. **Enable Auto-Scaling**
   - Create AMI from configured instance
   - Setup Auto Scaling Group
   - Configure load balancer

3. **Implement CI/CD**
   - Setup GitHub Actions
   - Auto-deploy on code push
   - Run automated tests

4. **Enhanced Monitoring**
   - Setup Grafana dashboards
   - Configure PagerDuty alerts
   - Implement custom metrics

---

## 📚 Quick Reference

### Essential Commands

```bash
# Start all services
./start-ec2.sh

# Stop all services
pkill -f python3

# View logs
tail -f logs/*.log

# Check service status
sudo systemctl status disaster-recovery

# Restart services
sudo systemctl restart disaster-recovery

# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

### Important URLs

- **Dashboard:** http://YOUR-EC2-IP:8080
- **AWS Console:** https://console.aws.amazon.com
- **CloudWatch Logs:** https://console.aws.amazon.com/cloudwatch

---

## ✅ Success Checklist

- [ ] EC2 instance launched successfully
- [ ] SSH connection working
- [ ] Python environment setup complete
- [ ] All dependencies installed
- [ ] AI models running
- [ ] Dashboard accessible from browser
- [ ] Security groups configured properly
- [ ] Monitoring enabled
- [ ] Backup strategy in place

---

**Last Updated:** February 2026  
**Version:** 1.0.0
