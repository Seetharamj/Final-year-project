# Manual EC2 Setup with Git Clone - Step by Step Guide

## 🎯 Overview
This guide walks you through manually creating an EC2 instance, cloning your project using Git, and running it on the server.

---

## 📋 Prerequisites

Before you start, make sure you have:
- ✅ AWS Account with access to EC2
- ✅ Your project code in a Git repository (GitHub, GitLab, etc.)
- ✅ SSH client on your local machine (Windows PowerShell, PuTTY, or Git Bash)

---

## 🚀 Step-by-Step Instructions

### **Step 1: Create EC2 Instance Manually**

1. **Login to AWS Console**
   - Go to: https://console.aws.amazon.com
   - Navigate to: **EC2 Dashboard**

2. **Launch Instance**
   - Click: **"Launch Instance"** button
   
3. **Configure Instance:**

   **Name and Tags:**
   ```
   Name: disaster-recovery-system
   ```

   **Application and OS Images (AMI):**
   ```
   AMI: Ubuntu Server 22.04 LTS (Free Tier eligible)
   Architecture: 64-bit (x86)
   ```

   **Instance Type:**
   ```
   Recommended: t2.medium (2 vCPU, 4 GB RAM)
   Minimum: t2.small (1 vCPU, 2 GB RAM)
   Budget: t2.micro (1 vCPU, 1 GB RAM) - may be slow
   ```

   **Key Pair (login):**
   ```
   - Click "Create new key pair"
   - Key pair name: disaster-recovery-key
   - Key pair type: RSA
   - Private key file format: .pem (for Mac/Linux) or .ppk (for PuTTY)
   - Click "Create key pair"
   - IMPORTANT: Save the downloaded .pem file securely!
   ```

   **Network Settings:**
   ```
   ✅ Create security group
   Security group name: disaster-recovery-sg
   
   Inbound Security Group Rules:
   1. SSH
      - Type: SSH
      - Port: 22
      - Source: My IP (your current IP)
   
   2. HTTP
      - Type: HTTP
      - Port: 80
      - Source: Anywhere (0.0.0.0/0)
   
   3. Custom TCP (Dashboard)
      - Type: Custom TCP
      - Port: 8080
      - Source: Anywhere (0.0.0.0/0)
   
   4. Custom TCP (API)
      - Type: Custom TCP
      - Port: 5000
      - Source: Anywhere (0.0.0.0/0)
   ```

   **Configure Storage:**
   ```
   Size: 20 GB
   Volume Type: gp3 (General Purpose SSD)
   ```

4. **Review and Launch**
   - Review all settings
   - Click **"Launch Instance"**
   - Wait for instance to be in **"Running"** state (2-3 minutes)

5. **Get Instance Details**
   - Click on your instance ID
   - Note down:
     - **Public IPv4 address** (e.g., 54.123.45.67)
     - **Public IPv4 DNS** (e.g., ec2-54-123-45-67.compute-1.amazonaws.com)

---

### **Step 2: Connect to EC2 Instance**

#### **Option A: Using Windows PowerShell**

1. **Set Key Permissions** (First time only)
   ```powershell
   # Navigate to where you saved the key
   cd C:\Users\naksh\Downloads
   
   # On Windows, right-click the .pem file
   # Properties → Security → Advanced → Disable inheritance → Remove all permissions
   # Add → Select your user → Full control → OK
   ```

2. **Connect via SSH**
   ```powershell
   # Replace with your actual key file and EC2 public IP
   ssh -i "disaster-recovery-key.pem" ubuntu@54.123.45.67
   
   # Or use the public DNS
   ssh -i "disaster-recovery-key.pem" ubuntu@ec2-54-123-45-67.compute-1.amazonaws.com
   ```

3. **Accept Fingerprint**
   ```
   Type: yes
   ```

#### **Option B: Using PuTTY (Windows)**

1. **Convert .pem to .ppk** (if you downloaded .pem)
   - Open **PuTTYgen**
   - Load your .pem file
   - Click "Save private key"
   - Save as .ppk file

2. **Connect with PuTTY**
   - Open **PuTTY**
   - Host Name: `ubuntu@54.123.45.67`
   - Port: `22`
   - Connection → SSH → Auth → Browse → Select your .ppk file
   - Click **Open**

---

### **Step 3: Setup EC2 Environment**

Once connected to your EC2 instance, run these commands:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install -y python3 python3-pip python3-venv

# Install Git
sudo apt install -y git

# Install additional useful tools
sudo apt install -y htop curl wget unzip

# Verify installations
python3 --version
pip3 --version
git --version
```

**Expected Output:**
```
Python 3.10.x or higher
pip 22.x or higher
git version 2.34.x or higher
```

---

### **Step 4: Clone Your Project from Git**

#### **Option A: Public Repository**

```bash
# Navigate to home directory
cd ~

# Clone your repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git project-1

# Navigate to project
cd project-1
```

#### **Option B: Private Repository**

**Method 1: Using Personal Access Token (Recommended)**

```bash
# Clone with token
git clone https://YOUR-TOKEN@github.com/YOUR-USERNAME/YOUR-REPO-NAME.git project-1
```

**Method 2: Using SSH Key**

```bash
# Generate SSH key on EC2
ssh-keygen -t ed25519 -C "your-email@example.com"

# Display public key
cat ~/.ssh/id_ed25519.pub

# Copy the output and add it to GitHub:
# GitHub → Settings → SSH and GPG keys → New SSH key → Paste key

# Clone repository
git clone git@github.com:YOUR-USERNAME/YOUR-REPO-NAME.git project-1
```

#### **Option C: Upload from Local Machine**

If you don't have your project in Git yet:

```powershell
# On your local Windows machine
scp -i "disaster-recovery-key.pem" -r C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1 ubuntu@54.123.45.67:~/
```

---

### **Step 5: Setup Python Environment**

```bash
# Navigate to project directory
cd ~/project-1

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) in your prompt now

# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes depending on your instance type and dependencies.

---

### **Step 6: Make Scripts Executable**

```bash
# Make setup and start scripts executable
chmod +x setup-ec2.sh
chmod +x start-ec2.sh

# Create logs directory
mkdir -p logs
```

---

### **Step 7: Run the System**

```bash
# Start all services
./start-ec2.sh
```

**Expected Output:**
```
========================================
Starting Disaster Recovery System
========================================
Stopping existing services...
✓ Stopped existing services
Activating virtual environment...
✓ Virtual environment activated
Starting Anomaly Detection Model...
✓ Anomaly Detection Model is running
  Log: logs/anomaly-detector.log
Starting Service Degradation Predictor...
✓ Degradation Predictor is running
  Log: logs/degradation-predictor.log
Starting Dashboard...
✓ Dashboard is running
  Log: logs/dashboard.log

========================================
System Status
========================================
Dashboard URL: http://54.123.45.67:8080

Service Status:
✓ Anomaly Detection is running
✓ Degradation Predictor is running
✓ Dashboard is running

========================================
Useful Commands:
========================================
View logs:           tail -f logs/*.log
Stop all services:   pkill -f python3
Restart services:    ./start-ec2.sh
Check processes:     ps aux | grep python

✓ Startup complete!
```

---

### **Step 8: Access the Dashboard**

1. **Open your web browser**
2. **Navigate to:**
   ```
   http://YOUR-EC2-PUBLIC-IP:8080
   ```
   Example: `http://54.123.45.67:8080`

3. **You should see the Disaster Recovery Dashboard!**

---

## 🔍 Verification & Testing

### Check Running Services

```bash
# Check all Python processes
ps aux | grep python

# Check specific services
ps aux | grep detector.py
ps aux | grep predictor.py
ps aux | grep "http.server"

# Check if port 8080 is listening
sudo netstat -tlnp | grep 8080
```

### View Logs

```bash
# View all logs in real-time
tail -f logs/*.log

# View specific log
tail -f logs/dashboard.log
tail -f logs/anomaly-detector.log
tail -f logs/degradation-predictor.log

# View last 50 lines of a log
tail -n 50 logs/dashboard.log
```

### Test Dashboard Locally on EC2

```bash
# Test from EC2 instance itself
curl http://localhost:8080

# Should return HTML content
```

### Get Public IP

```bash
# Get your EC2 public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

---

## 🛠️ Common Issues & Solutions

### Issue 1: Cannot Connect to EC2 via SSH

**Symptoms:**
```
Connection timed out
Permission denied
```

**Solutions:**

```bash
# 1. Check security group allows your IP on port 22
# AWS Console → EC2 → Security Groups → Check Inbound Rules

# 2. Verify key file permissions (on Windows)
# Right-click .pem → Properties → Security → Only your user should have access

# 3. Use verbose mode to debug
ssh -v -i "disaster-recovery-key.pem" ubuntu@YOUR-EC2-IP

# 4. Verify instance is running
# AWS Console → EC2 → Instances → Check state is "Running"
```

---

### Issue 2: Dashboard Not Accessible from Browser

**Symptoms:**
```
This site can't be reached
Connection refused
```

**Solutions:**

```bash
# 1. Check if dashboard is running
ps aux | grep "http.server"

# 2. Check if port 8080 is listening
sudo netstat -tlnp | grep 8080

# 3. Verify security group allows port 8080
# AWS Console → EC2 → Security Groups → Inbound Rules
# Should have: Custom TCP, Port 8080, Source 0.0.0.0/0

# 4. Test locally on EC2 first
curl http://localhost:8080

# 5. Restart the dashboard
pkill -f "http.server"
cd ~/project-1
./start-ec2.sh
```

---

### Issue 3: Services Not Starting

**Symptoms:**
```
✗ Anomaly Detection Model is not running
✗ Degradation Predictor is not running
```

**Solutions:**

```bash
# 1. Check Python version
python3 --version
# Should be 3.9 or higher

# 2. Verify virtual environment is activated
source ~/project-1/venv/bin/activate
which python
# Should show: /home/ubuntu/project-1/venv/bin/python

# 3. Check for errors in logs
cat logs/anomaly-detector.log
cat logs/degradation-predictor.log

# 4. Reinstall dependencies
cd ~/project-1
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# 5. Run services manually to see errors
python3 ai-models/anomaly-detection/isolation-forest/detector.py
```

---

### Issue 4: Out of Memory

**Symptoms:**
```
Killed
MemoryError
```

**Solutions:**

```bash
# 1. Check memory usage
free -h

# 2. Check which process is using memory
htop
# Press F6 to sort by MEM%

# 3. Upgrade instance type
# AWS Console → EC2 → Instance → Actions → Instance Settings → Change Instance Type
# Recommended: t2.medium (4 GB RAM)

# 4. Add swap space (temporary fix)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

### Issue 5: Git Clone Failed

**Symptoms:**
```
Permission denied (publickey)
fatal: Authentication failed
```

**Solutions:**

```bash
# For HTTPS (use personal access token)
git clone https://YOUR-TOKEN@github.com/YOUR-USERNAME/YOUR-REPO.git project-1

# For SSH (setup SSH key)
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub → Settings → SSH and GPG keys

# Or upload project manually from local machine
# On Windows PowerShell:
scp -i "disaster-recovery-key.pem" -r C:\path\to\project-1 ubuntu@YOUR-EC2-IP:~/
```

---

## 🔄 Keeping Services Running

### Option 1: Using nohup (Already configured in start-ec2.sh)

Services will keep running even after you disconnect from SSH.

```bash
# Start services
./start-ec2.sh

# Disconnect from SSH (services keep running)
exit

# Reconnect later
ssh -i "disaster-recovery-key.pem" ubuntu@YOUR-EC2-IP

# Check if services are still running
ps aux | grep python
```

---

### Option 2: Using systemd (Auto-start on boot)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/disaster-recovery.service
```

**Paste this content:**
```ini
[Unit]
Description=AI-Driven Disaster Recovery System
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/project-1
ExecStart=/home/ubuntu/project-1/start-ec2.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Save and exit:** `Ctrl+X`, then `Y`, then `Enter`

**Enable and start service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (auto-start on boot)
sudo systemctl enable disaster-recovery

# Start service now
sudo systemctl start disaster-recovery

# Check status
sudo systemctl status disaster-recovery

# View service logs
sudo journalctl -u disaster-recovery -f
```

**Useful systemd commands:**
```bash
# Stop service
sudo systemctl stop disaster-recovery

# Restart service
sudo systemctl restart disaster-recovery

# Disable auto-start
sudo systemctl disable disaster-recovery
```

---

## 📊 Monitoring Your System

### Check System Resources

```bash
# CPU and Memory usage (interactive)
htop

# Disk usage
df -h

# Check specific directory size
du -sh ~/project-1

# Network connections
sudo netstat -tlnp

# System uptime
uptime
```

### Monitor Logs in Real-time

```bash
# All logs
tail -f logs/*.log

# Specific log
tail -f logs/dashboard.log

# Last 100 lines
tail -n 100 logs/anomaly-detector.log

# Search logs for errors
grep -i error logs/*.log
```

---

## 🛑 Stopping Services

### Stop All Services

```bash
# Kill all Python processes
pkill -f python3

# Or if using systemd
sudo systemctl stop disaster-recovery

# Verify all stopped
ps aux | grep python
```

### Stop Specific Service

```bash
# Find process ID
ps aux | grep detector.py

# Kill specific process
kill -9 <PID>

# Example:
# ps aux shows: ubuntu  12345  ... detector.py
kill -9 12345
```

---

## 💰 Cost Management

### Estimated Monthly Costs

| Instance Type | vCPU | RAM | Storage | Total/Month |
|---------------|------|-----|---------|-------------|
| t2.micro      | 1    | 1GB | 20GB    | ~$10        |
| t2.small      | 1    | 2GB | 20GB    | ~$20        |
| t2.medium     | 2    | 4GB | 20GB    | ~$35        |

### Save Money

```bash
# Stop instance when not in use (you only pay for storage)
# AWS Console → EC2 → Instance → Actions → Stop Instance

# Start instance when needed
# AWS Console → EC2 → Instance → Actions → Start Instance

# Or use AWS CLI
aws ec2 stop-instances --instance-ids i-YOUR-INSTANCE-ID
aws ec2 start-instances --instance-ids i-YOUR-INSTANCE-ID
```

**Note:** When you stop and start, the public IP changes unless you use an Elastic IP.

---

## 🔒 Security Best Practices

### 1. Restrict SSH Access

```bash
# Only allow your IP for SSH
# AWS Console → EC2 → Security Groups → Edit Inbound Rules
# SSH (22) → Source: My IP (instead of 0.0.0.0/0)
```

### 2. Setup Firewall (UFW)

```bash
# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow Dashboard
sudo ufw allow 8080/tcp

# Check status
sudo ufw status
```

### 3. Regular Updates

```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd ~/project-1
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 4. Setup SSL/HTTPS (Optional)

```bash
# Install Nginx
sudo apt install nginx -y

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com
```

---

## 🧹 Cleanup & Termination

### Remove Everything

```bash
# 1. Stop all services
pkill -f python3

# 2. Remove systemd service (if created)
sudo systemctl stop disaster-recovery
sudo systemctl disable disaster-recovery
sudo rm /etc/systemd/system/disaster-recovery.service
sudo systemctl daemon-reload

# 3. Remove project files
rm -rf ~/project-1

# 4. Terminate EC2 instance
# AWS Console → EC2 → Instances → Select Instance → Actions → Terminate Instance
```

---

## 📚 Quick Command Reference

```bash
# Connect to EC2
ssh -i "disaster-recovery-key.pem" ubuntu@YOUR-EC2-IP

# Navigate to project
cd ~/project-1

# Activate virtual environment
source venv/bin/activate

# Start all services
./start-ec2.sh

# Stop all services
pkill -f python3

# View logs
tail -f logs/*.log

# Check running services
ps aux | grep python

# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Check system resources
htop
df -h
free -h

# Update project from Git
git pull origin main

# Restart services
pkill -f python3 && ./start-ec2.sh
```

---

## ✅ Success Checklist

- [ ] EC2 instance created and running
- [ ] SSH connection successful
- [ ] Python 3.9+ installed
- [ ] Git installed
- [ ] Project cloned from Git repository
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Scripts made executable
- [ ] All services started successfully
- [ ] Dashboard accessible from browser
- [ ] Security group configured properly
- [ ] Services keep running after SSH disconnect

---

## 🎓 Next Steps

1. **Setup Domain Name** (Optional)
   - Register a domain (e.g., from Namecheap, GoDaddy)
   - Point domain to EC2 Elastic IP
   - Setup SSL certificate with Certbot

2. **Multi-Region Deployment**
   - Follow the same steps in different AWS regions
   - Setup load balancer
   - Configure cross-region replication

3. **Monitoring & Alerts**
   - Setup CloudWatch monitoring
   - Configure email alerts
   - Create custom dashboards

4. **Backup Strategy**
   - Create AMI snapshots
   - Setup automated backups
   - Test disaster recovery procedures

---

## 📞 Support & Resources

- **AWS EC2 Documentation:** https://docs.aws.amazon.com/ec2/
- **Ubuntu Server Guide:** https://ubuntu.com/server/docs
- **Git Documentation:** https://git-scm.com/doc
- **Python Virtual Environments:** https://docs.python.org/3/library/venv.html

---

**Last Updated:** February 2026  
**Version:** 1.0.0  
**Author:** Disaster Recovery System Team
