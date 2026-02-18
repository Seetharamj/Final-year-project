# EC2 Quick Start Guide

## 🚀 Fastest Way to Run on EC2

### Option 1: Manual Upload (Recommended for First Time)

1. **Launch EC2 Instance:**
   ```
   - Go to AWS Console → EC2 → Launch Instance
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t2.medium
   - Security Group: Allow ports 22, 80, 8080
   - Launch and download key pair
   ```

2. **Upload Project to EC2:**
   ```powershell
   # From your Windows machine
   scp -i "your-key.pem" -r c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1 ubuntu@YOUR-EC2-IP:~/
   ```

3. **Connect to EC2:**
   ```powershell
   ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP
   ```

4. **Run Setup:**
   ```bash
   cd ~/project-1
   chmod +x setup-ec2.sh
   ./setup-ec2.sh
   ```

5. **Start System:**
   ```bash
   ./start-ec2.sh
   ```

6. **Access Dashboard:**
   ```
   http://YOUR-EC2-IP:8080
   ```

---

## Option 2: Using Terraform (Multi-Region)

1. **Deploy Infrastructure:**
   ```powershell
   cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\infrastructure\terraform
   terraform init
   terraform apply
   ```

2. **Get EC2 IPs:**
   ```powershell
   terraform output
   ```

3. **Upload to Each Instance:**
   ```powershell
   # Repeat for each region
   scp -i "your-key.pem" -r project-1 ubuntu@EC2-IP:~/
   ```

4. **Setup Each Instance:**
   ```bash
   ssh -i "your-key.pem" ubuntu@EC2-IP
   cd ~/project-1
   ./setup-ec2.sh
   ./start-ec2.sh
   ```

---

## 📋 Essential Commands

### On Your Local Machine (Windows)

```powershell
# Upload project to EC2
scp -i "your-key.pem" -r c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1 ubuntu@YOUR-EC2-IP:~/

# Connect to EC2
ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP

# Check EC2 status
aws ec2 describe-instances --instance-ids i-xxxxx

# Get EC2 public IP
aws ec2 describe-instances --instance-ids i-xxxxx --query 'Reservations[0].Instances[0].PublicIpAddress'
```

### On EC2 Instance (Linux)

```bash
# Navigate to project
cd ~/project-1

# Setup environment (first time only)
./setup-ec2.sh

# Start all services
./start-ec2.sh

# Stop all services
pkill -f python3

# View logs
tail -f logs/*.log

# Check running processes
ps aux | grep python

# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Check disk space
df -h

# Check memory usage
free -h

# Monitor resources
htop
```

### Using Systemd Service

```bash
# Start service
sudo systemctl start disaster-recovery

# Stop service
sudo systemctl stop disaster-recovery

# Check status
sudo systemctl status disaster-recovery

# Enable auto-start on boot
sudo systemctl enable disaster-recovery

# View service logs
sudo journalctl -u disaster-recovery -f
```

---

## 🔧 Troubleshooting

### Cannot Connect to EC2

```bash
# Check security group allows your IP on port 22
# Verify key permissions
chmod 400 your-key.pem

# Test connection
ssh -v -i "your-key.pem" ubuntu@YOUR-EC2-IP
```

### Dashboard Not Accessible

```bash
# Check if service is running
ps aux | grep "http.server"

# Check port 8080 is open
sudo netstat -tlnp | grep 8080

# Check security group allows port 8080
# AWS Console → EC2 → Security Groups → Inbound Rules
```

### Services Not Starting

```bash
# Check Python version
python3 --version

# Activate virtual environment
source ~/project-1/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check logs for errors
tail -f ~/project-1/logs/*.log
```

### Out of Memory

```bash
# Check memory usage
free -h

# Upgrade to larger instance type
# AWS Console → EC2 → Actions → Instance Settings → Change Instance Type
```

---

## 💰 Cost Estimate

| Instance Type | vCPU | RAM | Cost/Month | Use Case |
|---------------|------|-----|------------|----------|
| t2.micro | 1 | 1 GB | ~$8 | Testing only |
| t2.small | 1 | 2 GB | ~$17 | Light usage |
| t2.medium | 2 | 4 GB | ~$34 | Recommended |
| t2.large | 2 | 8 GB | ~$68 | Heavy usage |

**Additional Costs:**
- Storage (20 GB): ~$2/month
- Data Transfer: ~$5-20/month
- **Total: ~$20-100/month**

---

## 🎯 Quick Checklist

**Before Starting:**
- [ ] AWS account created
- [ ] EC2 key pair downloaded
- [ ] Security group configured (ports 22, 80, 8080)
- [ ] Project files ready

**After EC2 Launch:**
- [ ] Connected via SSH
- [ ] Project uploaded
- [ ] Dependencies installed
- [ ] Services running
- [ ] Dashboard accessible

**For Production:**
- [ ] SSL certificate installed
- [ ] Domain name configured
- [ ] Auto-scaling enabled
- [ ] Backups configured
- [ ] Monitoring enabled

---

## 📞 Support Resources

- **AWS Documentation:** https://docs.aws.amazon.com/ec2/
- **Ubuntu Server Guide:** https://ubuntu.com/server/docs
- **Python Virtual Environments:** https://docs.python.org/3/library/venv.html

---

## 🔗 Important URLs

After deployment, save these URLs:

```
Dashboard:     http://YOUR-EC2-IP:8080
AWS Console:   https://console.aws.amazon.com/ec2/
SSH Command:   ssh -i "your-key.pem" ubuntu@YOUR-EC2-IP
```

---

**Last Updated:** February 2026
