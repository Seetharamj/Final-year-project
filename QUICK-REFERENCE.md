# Quick Reference Card - EC2 Deployment

## 🚀 5-Minute Quick Start

### 1. Create EC2 Instance
```
AWS Console → EC2 → Launch Instance
- AMI: Ubuntu 22.04 LTS
- Type: t2.medium
- Security: Ports 22, 80, 8080
- Download key pair
```

### 2. Connect
```powershell
ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP
```

### 3. Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
cd ~
git clone YOUR-REPO-URL project-1
cd project-1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x start-ec2.sh
```

### 4. Run
```bash
./start-ec2.sh
```

### 5. Access
```
http://YOUR-EC2-IP:8080
```

---

## 📋 Essential Commands

### Connection
```bash
# Connect to EC2
ssh -i "disaster-recovery-key.pem" ubuntu@YOUR-EC2-IP

# Upload files
scp -i "your-key.pem" -r /local/path ubuntu@YOUR-EC2-IP:~/

# Download files
scp -i "your-key.pem" ubuntu@YOUR-EC2-IP:~/file.txt /local/path
```

### Project Management
```bash
# Navigate to project
cd ~/project-1

# Activate environment
source venv/bin/activate

# Update from Git
git pull origin main

# Install new dependencies
pip install -r requirements.txt
```

### Service Control
```bash
# Start all services
./start-ec2.sh

# Stop all services
pkill -f python3

# Restart services
pkill -f python3 && ./start-ec2.sh

# Check running services
ps aux | grep python

# Check specific service
ps aux | grep detector.py
ps aux | grep predictor.py
ps aux | grep "http.server"
```

### Logs & Monitoring
```bash
# View all logs
tail -f logs/*.log

# View specific log
tail -f logs/dashboard.log
tail -f logs/anomaly-detector.log
tail -f logs/degradation-predictor.log

# Last 50 lines
tail -n 50 logs/dashboard.log

# Search for errors
grep -i error logs/*.log

# Clear logs
> logs/dashboard.log
```

### System Info
```bash
# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Check disk space
df -h

# Check memory
free -h

# Check CPU/Memory usage
htop

# System uptime
uptime

# Network connections
sudo netstat -tlnp
```

### Systemd Service (if configured)
```bash
# Start
sudo systemctl start disaster-recovery

# Stop
sudo systemctl stop disaster-recovery

# Restart
sudo systemctl restart disaster-recovery

# Status
sudo systemctl status disaster-recovery

# Enable auto-start
sudo systemctl enable disaster-recovery

# Disable auto-start
sudo systemctl disable disaster-recovery

# View logs
sudo journalctl -u disaster-recovery -f
```

---

## 🔧 Troubleshooting Quick Fixes

### Dashboard not accessible
```bash
# Check if running
ps aux | grep "http.server"

# Check port
sudo netstat -tlnp | grep 8080

# Restart
pkill -f "http.server"
cd ~/project-1 && ./start-ec2.sh
```

### Services not starting
```bash
# Check logs
cat logs/anomaly-detector.log
cat logs/degradation-predictor.log

# Reinstall dependencies
cd ~/project-1
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Run manually to see errors
python3 ai-models/anomaly-detection/isolation-forest/detector.py
```

### Out of memory
```bash
# Check memory
free -h

# Add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Or upgrade instance type in AWS Console
```

### SSH connection issues
```bash
# Check key permissions (Windows)
# Right-click .pem → Properties → Security → Only your user

# Verbose SSH
ssh -v -i "your-key.pem" ubuntu@YOUR-EC2-IP

# Check security group allows your IP on port 22
```

### Git clone failed
```bash
# Use HTTPS with token
git clone https://YOUR-TOKEN@github.com/USER/REPO.git project-1

# Or setup SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"
cat ~/.ssh/id_ed25519.pub
# Add to GitHub → Settings → SSH keys
```

---

## 🌍 Multi-Region Deployment

### Deploy to 3 Regions
```bash
# Region 1: us-east-1 (N. Virginia)
# Region 2: us-west-2 (Oregon)
# Region 3: eu-west-1 (Ireland)

# For each region:
1. Create EC2 instance
2. SSH and setup
3. Clone project
4. Run ./start-ec2.sh
5. Verify dashboard accessible
```

### Quick Region Setup Script
```bash
#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
cd ~
git clone YOUR-REPO-URL project-1
cd project-1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
chmod +x start-ec2.sh
./start-ec2.sh
```

---

## 💰 Cost Management

### Stop Instance (save money)
```bash
# AWS Console → EC2 → Instance → Actions → Stop
# Or via CLI:
aws ec2 stop-instances --instance-ids i-YOUR-ID
```

### Start Instance
```bash
# AWS Console → EC2 → Instance → Actions → Start
# Or via CLI:
aws ec2 start-instances --instance-ids i-YOUR-ID
```

### Check Costs
```bash
# AWS Console → Billing Dashboard → Cost Explorer
```

---

## 🔒 Security Checklist

- [ ] SSH restricted to your IP only
- [ ] Strong key pair used
- [ ] Regular system updates (`sudo apt update && sudo apt upgrade`)
- [ ] Firewall enabled (`sudo ufw enable`)
- [ ] Unnecessary ports closed
- [ ] SSL/HTTPS configured (for production)
- [ ] Regular backups enabled

---

## 📊 Performance Optimization

### Check Performance
```bash
# CPU usage
top

# Memory usage
free -h

# Disk I/O
iostat

# Network
iftop
```

### Optimize
```bash
# Clear cache
sudo sync; echo 3 | sudo tee /proc/sys/vm/drop_caches

# Kill unused processes
pkill -f <process-name>

# Upgrade instance type if needed
# AWS Console → EC2 → Actions → Instance Settings → Change Instance Type
```

---

## 🎯 Important URLs

| Service | URL |
|---------|-----|
| Dashboard | http://YOUR-EC2-IP:8080 |
| AWS Console | https://console.aws.amazon.com/ec2/ |
| CloudWatch | https://console.aws.amazon.com/cloudwatch/ |
| Billing | https://console.aws.amazon.com/billing/ |

---

## 📞 Emergency Commands

### System completely frozen
```bash
# Force restart instance
# AWS Console → EC2 → Instance → Actions → Reboot
```

### Disk full
```bash
# Find large files
du -sh /* | sort -h

# Clear logs
sudo journalctl --vacuum-time=3d

# Clear apt cache
sudo apt clean
```

### Can't SSH
```bash
# Use EC2 Instance Connect (browser-based)
# AWS Console → EC2 → Instance → Connect → EC2 Instance Connect
```

---

## ✅ Daily Checklist

**Morning:**
- [ ] Check all services running: `ps aux | grep python`
- [ ] Check dashboard accessible
- [ ] Review logs for errors: `grep -i error logs/*.log`
- [ ] Check disk space: `df -h`

**Evening:**
- [ ] Backup important data
- [ ] Check system updates: `sudo apt update`
- [ ] Review CloudWatch metrics
- [ ] Stop instance if not needed overnight

---

## 🎓 Useful Aliases (Optional)

Add to `~/.bashrc`:
```bash
# Project shortcuts
alias proj='cd ~/project-1'
alias venv='source ~/project-1/venv/bin/activate'
alias start='cd ~/project-1 && ./start-ec2.sh'
alias stop='pkill -f python3'
alias logs='tail -f ~/project-1/logs/*.log'
alias status='ps aux | grep python'

# System shortcuts
alias update='sudo apt update && sudo apt upgrade -y'
alias myip='curl http://169.254.169.254/latest/meta-data/public-ipv4'
```

Then run: `source ~/.bashrc`

---

**Last Updated:** February 2026  
**Keep this handy for quick reference!**
