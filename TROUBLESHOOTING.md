# EC2 Deployment Troubleshooting Guide

## 🔧 Common Issues and Solutions

This guide covers the most common issues you'll encounter when deploying to EC2 and how to fix them.

---

## Table of Contents

1. [SSH Connection Issues](#ssh-connection-issues)
2. [Git Clone Problems](#git-clone-problems)
3. [Python Environment Issues](#python-environment-issues)
4. [Service Startup Failures](#service-startup-failures)
5. [Dashboard Not Accessible](#dashboard-not-accessible)
6. [Performance Issues](#performance-issues)
7. [Storage Issues](#storage-issues)
8. [Network Issues](#network-issues)
9. [AWS-Specific Issues](#aws-specific-issues)

---

## SSH Connection Issues

### Problem 1: "Permission denied (publickey)"

**Symptoms:**
```
ubuntu@ec2-xx-xx-xx-xx.compute-1.amazonaws.com: Permission denied (publickey).
```

**Solutions:**

```bash
# 1. Check you're using the correct key file
ssh -i "disaster-recovery-key.pem" ubuntu@YOUR-EC2-IP

# 2. Verify key file permissions (Linux/Mac)
chmod 400 disaster-recovery-key.pem

# 3. On Windows, set permissions:
# Right-click .pem file → Properties → Security → Advanced
# - Disable inheritance
# - Remove all users except your account
# - Give your account Full Control

# 4. Verify you're using the correct username
# For Ubuntu AMI: ubuntu
# For Amazon Linux: ec2-user
# For RHEL: ec2-user
ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP

# 5. Use verbose mode to debug
ssh -v -i "your-key.pem" ubuntu@YOUR-EC2-IP
```

---

### Problem 2: "Connection timed out"

**Symptoms:**
```
ssh: connect to host ec2-xx-xx-xx-xx.compute-1.amazonaws.com port 22: Connection timed out
```

**Solutions:**

```bash
# 1. Check instance is running
# AWS Console → EC2 → Instances → Check state is "Running"

# 2. Verify security group allows SSH from your IP
# AWS Console → EC2 → Security Groups → Inbound Rules
# Should have: SSH (22), Source: Your IP or 0.0.0.0/0

# 3. Check your current public IP
curl ifconfig.me

# 4. Update security group with your current IP
# AWS Console → EC2 → Security Groups → Edit Inbound Rules
# SSH (22) → Source → My IP

# 5. Try using the public IP instead of DNS
ssh -i "your-key.pem" ubuntu@54.123.45.67

# 6. Check if your firewall is blocking SSH
# Windows: Check Windows Firewall settings
# Mac/Linux: Check iptables or firewall settings
```

---

### Problem 3: "Host key verification failed"

**Symptoms:**
```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
```

**Solutions:**

```bash
# This happens when you stop/start an instance and get a new IP

# 1. Remove old host key (Linux/Mac)
ssh-keygen -R ec2-xx-xx-xx-xx.compute-1.amazonaws.com
ssh-keygen -R 54.123.45.67

# 2. On Windows, delete the known_hosts file
# C:\Users\YourName\.ssh\known_hosts

# 3. Connect again and accept new fingerprint
ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP
# Type: yes
```

---

## Git Clone Problems

### Problem 1: "Permission denied (publickey)" when cloning

**Symptoms:**
```
git@github.com: Permission denied (publickey).
fatal: Could not read from remote repository.
```

**Solutions:**

```bash
# Option 1: Use HTTPS instead of SSH
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git project-1

# Option 2: Use Personal Access Token
git clone https://YOUR-TOKEN@github.com/YOUR-USERNAME/YOUR-REPO.git project-1

# Option 3: Setup SSH key on EC2
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
# Copy output and add to GitHub → Settings → SSH and GPG keys → New SSH key
git clone git@github.com:YOUR-USERNAME/YOUR-REPO.git project-1
```

---

### Problem 2: "Repository not found"

**Symptoms:**
```
fatal: repository 'https://github.com/USER/REPO.git/' not found
```

**Solutions:**

```bash
# 1. Verify repository URL is correct
# Go to GitHub → Your Repo → Code → Copy HTTPS URL

# 2. For private repos, use token
git clone https://YOUR-TOKEN@github.com/YOUR-USERNAME/YOUR-REPO.git project-1

# 3. Check repository exists and you have access
# Open in browser: https://github.com/YOUR-USERNAME/YOUR-REPO
```

---

### Problem 3: "fatal: unable to access" (SSL/Network issues)

**Symptoms:**
```
fatal: unable to access 'https://github.com/...': Could not resolve host
```

**Solutions:**

```bash
# 1. Check internet connectivity
ping google.com

# 2. Check DNS resolution
nslookup github.com

# 3. Update git configuration
git config --global http.sslVerify false  # Only for testing!

# 4. Use different DNS
sudo nano /etc/resolv.conf
# Add: nameserver 8.8.8.8

# 5. Check if GitHub is down
curl https://www.githubstatus.com/
```

---

## Python Environment Issues

### Problem 1: "python3: command not found"

**Symptoms:**
```
bash: python3: command not found
```

**Solutions:**

```bash
# 1. Install Python
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. Verify installation
python3 --version
which python3

# 3. If still not found, check PATH
echo $PATH

# 4. Create symlink if needed
sudo ln -s /usr/bin/python3.10 /usr/bin/python3
```

---

### Problem 2: "No module named 'venv'"

**Symptoms:**
```
Error: No module named 'venv'
```

**Solutions:**

```bash
# Install python3-venv package
sudo apt update
sudo apt install -y python3-venv

# Verify installation
python3 -m venv --help
```

---

### Problem 3: pip install fails with "externally-managed-environment"

**Symptoms:**
```
error: externally-managed-environment
```

**Solutions:**

```bash
# This is why we use virtual environments!

# 1. Always use virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Now install packages
pip install -r requirements.txt

# 3. Verify you're in venv
which python
# Should show: /home/ubuntu/project-1/venv/bin/python
```

---

### Problem 4: pip install takes forever or fails

**Symptoms:**
```
Building wheel for tensorflow (setup.py) ... [hangs]
```

**Solutions:**

```bash
# 1. Upgrade pip first
pip install --upgrade pip

# 2. Use binary wheels (faster)
pip install --only-binary=:all: -r requirements.txt

# 3. Install packages one by one to identify problem
pip install numpy
pip install pandas
pip install scikit-learn
# etc.

# 4. Increase timeout
pip install --timeout=1000 -r requirements.txt

# 5. Use lighter alternatives for testing
# Comment out heavy packages in requirements.txt:
# tensorflow>=2.13.0  # Comment this out
# torch>=2.0.0        # Comment this out

# 6. Upgrade instance type if t2.micro
# t2.micro (1GB RAM) struggles with large packages
# Use t2.small (2GB) or t2.medium (4GB)
```

---

## Service Startup Failures

### Problem 1: "detector.py not found"

**Symptoms:**
```
python3: can't open file 'ai-models/anomaly-detection/isolation-forest/detector.py': [Errno 2] No such file or directory
```

**Solutions:**

```bash
# 1. Verify you're in the project directory
pwd
# Should show: /home/ubuntu/project-1

# 2. Check if file exists
ls -la ai-models/anomaly-detection/isolation-forest/detector.py

# 3. Check project structure
tree -L 3  # or use: find . -name "*.py"

# 4. If files are missing, re-clone
cd ~
rm -rf project-1
git clone YOUR-REPO-URL project-1

# 5. Or upload from local machine
# On Windows:
scp -i "your-key.pem" -r C:\path\to\project-1 ubuntu@YOUR-EC2-IP:~/
```

---

### Problem 2: Services start but immediately stop

**Symptoms:**
```
✓ Anomaly Detection Model is running
[2 seconds later]
✗ Anomaly Detection Model is not running
```

**Solutions:**

```bash
# 1. Check logs for errors
cat logs/anomaly-detector.log
cat logs/degradation-predictor.log

# 2. Run service manually to see errors
cd ~/project-1
source venv/bin/activate
python3 ai-models/anomaly-detection/isolation-forest/detector.py

# 3. Common errors and fixes:

# Error: ModuleNotFoundError
pip install -r requirements.txt

# Error: ImportError
# Check Python version
python3 --version  # Should be 3.9+

# Error: MemoryError
# Upgrade instance type or add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 4. Check if port is already in use
sudo lsof -i :8080
# If something is using it:
sudo kill -9 <PID>
```

---

### Problem 3: "Address already in use"

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solutions:**

```bash
# 1. Find process using the port
sudo lsof -i :8080

# 2. Kill the process
sudo kill -9 <PID>

# 3. Or kill all Python processes
pkill -f python3

# 4. Wait a few seconds and restart
sleep 3
./start-ec2.sh

# 5. Use different port if needed
# Edit start-ec2.sh and change 8080 to 8081
python3 -m http.server 8081
```

---

## Dashboard Not Accessible

### Problem 1: "This site can't be reached"

**Symptoms:**
Browser shows "This site can't be reached" or "Connection refused"

**Solutions:**

```bash
# 1. Verify dashboard is running on EC2
ps aux | grep "http.server"

# 2. Test locally on EC2
curl http://localhost:8080
# Should return HTML

# 3. Check security group allows port 8080
# AWS Console → EC2 → Security Groups → Inbound Rules
# Should have: Custom TCP, Port 8080, Source 0.0.0.0/0

# 4. Add security group rule if missing
# AWS Console → EC2 → Security Groups → Edit Inbound Rules
# Add Rule:
#   Type: Custom TCP
#   Port: 8080
#   Source: 0.0.0.0/0

# 5. Verify you're using the correct public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# 6. Try accessing with public IP instead of DNS
http://54.123.45.67:8080

# 7. Check if firewall is blocking
sudo ufw status
# If active, allow port 8080:
sudo ufw allow 8080/tcp
```

---

### Problem 2: Dashboard loads but shows no data

**Symptoms:**
Dashboard opens but shows empty charts or "No data available"

**Solutions:**

```bash
# 1. Check if AI models are running
ps aux | grep detector.py
ps aux | grep predictor.py

# 2. Check model logs for errors
tail -f logs/anomaly-detector.log
tail -f logs/degradation-predictor.log

# 3. Restart all services
pkill -f python3
./start-ec2.sh

# 4. Check if data files exist
ls -la data/
ls -la ai-models/*/data/

# 5. Run disaster simulation to generate data
cd ~/project-1
source venv/bin/activate
python3 disaster-simulator/runner.py
```

---

### Problem 3: Dashboard shows 404 errors

**Symptoms:**
Dashboard loads but CSS/JS files show 404 errors

**Solutions:**

```bash
# 1. Check dashboard directory structure
cd ~/project-1/dashboard/frontend
ls -la

# 2. Verify files exist
ls -la css/
ls -la js/

# 3. Check file permissions
chmod -R 755 ~/project-1/dashboard/frontend

# 4. Restart dashboard from correct directory
cd ~/project-1/dashboard/frontend
python3 -m http.server 8080

# 5. Check browser console for specific missing files
# Browser → F12 → Console → Look for 404 errors
```

---

## Performance Issues

### Problem 1: System is very slow

**Symptoms:**
Commands take forever, services are sluggish

**Solutions:**

```bash
# 1. Check CPU usage
top
# Press 'q' to quit

# 2. Check memory usage
free -h

# 3. Check disk usage
df -h

# 4. Check I/O wait
iostat

# 5. Identify resource-hungry processes
htop
# Press F6 to sort by CPU or MEM

# 6. Solutions:

# If CPU is maxed out:
# - Upgrade instance type (t2.medium → t2.large)
# - Reduce number of services running

# If memory is full:
# - Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# - Or upgrade instance type

# If disk is full:
# - Clean up logs
> logs/anomaly-detector.log
> logs/degradation-predictor.log
> logs/dashboard.log

# - Remove old packages
sudo apt autoremove
sudo apt clean
```

---

### Problem 2: Out of memory errors

**Symptoms:**
```
MemoryError
Killed
```

**Solutions:**

```bash
# 1. Check current memory usage
free -h

# 2. Check which process is using memory
ps aux --sort=-%mem | head

# 3. Add swap space (temporary fix)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Verify swap is active
free -h

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 4. Reduce memory usage:
# - Comment out heavy ML models in requirements.txt
# - Use lighter alternatives
# - Run fewer services simultaneously

# 5. Upgrade instance type (recommended)
# AWS Console → EC2 → Instance → Actions → Instance Settings
# → Change Instance Type → t2.medium or t2.large
```

---

## Storage Issues

### Problem 1: "No space left on device"

**Symptoms:**
```
OSError: [Errno 28] No space left on device
```

**Solutions:**

```bash
# 1. Check disk usage
df -h

# 2. Find large files/directories
du -sh /* | sort -h
du -sh ~/project-1/* | sort -h

# 3. Clean up:

# Clear logs
> logs/anomaly-detector.log
> logs/degradation-predictor.log
> logs/dashboard.log

# Clear system logs
sudo journalctl --vacuum-time=3d

# Clear apt cache
sudo apt clean
sudo apt autoremove

# Remove old kernels
sudo apt autoremove --purge

# 4. Increase EBS volume size
# AWS Console → EC2 → Volumes → Select Volume → Actions → Modify Volume
# Increase size (e.g., 20GB → 30GB)

# Then resize filesystem on EC2:
sudo growpart /dev/xvda 1
sudo resize2fs /dev/xvda1

# Verify new size
df -h
```

---

## Network Issues

### Problem 1: Can't reach external services

**Symptoms:**
```
curl: (6) Could not resolve host: github.com
```

**Solutions:**

```bash
# 1. Check internet connectivity
ping 8.8.8.8

# 2. Check DNS resolution
nslookup github.com

# 3. Update DNS servers
sudo nano /etc/resolv.conf
# Add:
nameserver 8.8.8.8
nameserver 8.8.4.4

# 4. Restart networking
sudo systemctl restart systemd-resolved

# 5. Check route table
# AWS Console → VPC → Route Tables
# Should have route to Internet Gateway (0.0.0.0/0 → igw-xxx)

# 6. Verify instance has public IP
# AWS Console → EC2 → Instance → Check "Public IPv4 address"
```

---

## AWS-Specific Issues

### Problem 1: Instance state is "pending" forever

**Symptoms:**
Instance stuck in "pending" state for more than 5 minutes

**Solutions:**

```bash
# 1. Wait 10 minutes (sometimes AWS is slow)

# 2. Check AWS Service Health Dashboard
# https://status.aws.amazon.com/

# 3. Check instance status checks
# AWS Console → EC2 → Instance → Status Checks

# 4. If still pending after 15 minutes:
# - Stop the instance
# - Wait for "stopped" state
# - Start again

# 5. If that doesn't work:
# - Terminate instance
# - Create new instance
```

---

### Problem 2: Can't connect after stop/start

**Symptoms:**
After stopping and starting instance, SSH doesn't work

**Solutions:**

```bash
# Public IP changes when you stop/start!

# 1. Get new public IP
# AWS Console → EC2 → Instance → Public IPv4 address

# 2. Update SSH command with new IP
ssh -i "your-key.pem" ubuntu@NEW-EC2-IP

# 3. Remove old host key
ssh-keygen -R OLD-IP
ssh-keygen -R NEW-IP

# 4. To prevent IP changes, use Elastic IP:
# AWS Console → EC2 → Elastic IPs → Allocate Elastic IP
# → Associate with instance
```

---

### Problem 3: Billing charges higher than expected

**Symptoms:**
AWS bill is higher than estimated

**Solutions:**

```bash
# 1. Check Cost Explorer
# AWS Console → Billing → Cost Explorer

# 2. Common causes:
# - Instance running 24/7
# - Data transfer charges
# - EBS volume charges
# - Elastic IP not associated with running instance

# 3. Reduce costs:

# Stop instance when not in use
aws ec2 stop-instances --instance-ids i-YOUR-ID

# Delete unused volumes
# AWS Console → EC2 → Volumes → Delete unused volumes

# Release unused Elastic IPs
# AWS Console → EC2 → Elastic IPs → Release unused IPs

# Use smaller instance type
# t2.micro instead of t2.medium for testing

# Setup billing alerts
# AWS Console → Billing → Billing Preferences → Receive Billing Alerts
```

---

## Emergency Recovery

### Complete System Reset

If everything is broken and you want to start fresh:

```bash
# 1. On EC2, backup important data
cd ~
tar -czf backup.tar.gz project-1/logs project-1/data

# 2. Download backup to local machine (from Windows)
scp -i "your-key.pem" ubuntu@YOUR-EC2-IP:~/backup.tar.gz C:\backup\

# 3. On EC2, remove everything
cd ~
rm -rf project-1
rm -rf venv

# 4. Start fresh
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
git clone YOUR-REPO-URL project-1
cd project-1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x start-ec2.sh
./start-ec2.sh

# 5. Restore backup if needed
tar -xzf ~/backup.tar.gz -C ~/project-1/
```

---

### Create AMI Snapshot (Backup)

Save your working configuration:

```bash
# AWS Console → EC2 → Instance → Actions → Image and templates
# → Create image

# Name: disaster-recovery-working-v1
# Description: Working configuration from [date]

# To restore later:
# AWS Console → EC2 → AMIs → Select AMI → Launch instance from AMI
```

---

## Getting Help

### Collect Diagnostic Information

Before asking for help, collect this information:

```bash
# System info
uname -a
cat /etc/os-release

# Python info
python3 --version
pip --version

# Service status
ps aux | grep python

# Logs
tail -n 100 logs/anomaly-detector.log
tail -n 100 logs/degradation-predictor.log
tail -n 100 logs/dashboard.log

# System resources
free -h
df -h
top -bn1 | head -20

# Network
curl http://169.254.169.254/latest/meta-data/public-ipv4
sudo netstat -tlnp

# Save all to file
./collect-diagnostics.sh > diagnostics.txt
```

---

## Useful Debugging Commands

```bash
# Check all Python processes
ps aux | grep python

# Check specific port
sudo lsof -i :8080

# Check logs in real-time
tail -f logs/*.log

# Check system logs
sudo journalctl -xe

# Check service status (if using systemd)
sudo systemctl status disaster-recovery

# Network debugging
ping google.com
nslookup github.com
curl -I http://localhost:8080

# File permissions
ls -la ~/project-1/
ls -la ~/project-1/start-ec2.sh

# Disk usage
du -sh ~/project-1/*
df -h

# Memory usage
free -h
ps aux --sort=-%mem | head -10

# CPU usage
top -bn1 | head -20
ps aux --sort=-%cpu | head -10
```

---

**Last Updated:** February 2026  
**Version:** 1.0.0  
**Keep this guide handy for quick troubleshooting!**
