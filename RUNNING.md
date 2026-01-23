# Running the AI-Driven Cloud-Based Disaster Recovery System

This guide provides step-by-step instructions for running the disaster recovery system in different modes.

## Table of Contents
1. [Quick Start (Dashboard Only)](#quick-start-dashboard-only)
2. [Full Local Development](#full-local-development)
3. [Individual Components](#individual-components)
4. [Cloud Deployment](#cloud-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Dashboard Only)

The fastest way to see the system in action is to run the dashboard:

### Option 1: Using the Quick Start Script
```bash
# Double-click quick-start.bat or run in terminal:
quick-start.bat
```

### Option 2: Manual Steps
```bash
# Navigate to project directory
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1

# Go to dashboard frontend
cd dashboard\frontend

# Start HTTP server
python -m http.server 8080

# Open browser to http://localhost:8080
```

---

## Full Local Development

To run all components (AI models + Dashboard):

### Automated Startup (Recommended)
```powershell
# Run the automated startup script
.\run-local.ps1
```

This script will:
- ✓ Create and activate Python virtual environment
- ✓ Install all dependencies
- ✓ Start Anomaly Detection model
- ✓ Start Degradation Predictor model
- ✓ Start Dashboard server
- ✓ Open browser automatically

### Manual Startup

**Terminal 1: Anomaly Detection**
```bash
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1
.\venv\Scripts\activate
python ai-models\anomaly-detection\isolation-forest\detector.py
```

**Terminal 2: Degradation Predictor**
```bash
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1
.\venv\Scripts\activate
python ai-models\prediction\degradation-predictor\predictor.py
```

**Terminal 3: Dashboard**
```bash
cd c:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\dashboard\frontend
python -m http.server 8080
```

---

## Individual Components

### 1. Anomaly Detection Model

Detects unusual patterns in system metrics using Isolation Forest algorithm.

```bash
# Activate environment
.\venv\Scripts\activate

# Run detector
python ai-models\anomaly-detection\isolation-forest\detector.py
```

**Expected Output:**
- Model initialization messages
- Real-time anomaly detection results
- Confidence scores for detected anomalies

### 2. Service Degradation Predictor

Predicts potential service failures before they occur.

```bash
# Activate environment
.\venv\Scripts\activate

# Run predictor
python ai-models\prediction\degradation-predictor\predictor.py
```

**Expected Output:**
- Model loading confirmation
- Prediction results with timestamps
- Risk scores and recommendations

### 3. Dashboard

Interactive web interface for monitoring and control.

```bash
cd dashboard\frontend
python -m http.server 8080
```

**Access at:** http://localhost:8080

**Features:**
- Real-time system status
- Disaster scenario visualization
- Recovery progress tracking
- AI model insights
- Governance metrics

---

## Cloud Deployment

For production deployment to AWS:

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured (`aws configure`)
- Terraform installed

### Deployment Steps

**1. Configure AWS Credentials**
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region (e.g., us-east-1)
```

**2. Initialize Terraform**
```bash
cd infrastructure\terraform
terraform init
```

**3. Review Deployment Plan**
```bash
terraform plan
```

**4. Deploy Infrastructure**
```bash
terraform apply
# Type 'yes' when prompted
```

**5. Deploy Monitoring Stack**
```bash
cd ..\..\monitoring
# Follow monitoring-specific deployment instructions
```

**6. Deploy AI Models to Cloud**
```bash
# Package models
cd ..\..\ai-models
# Deploy using AWS Lambda or ECS
```

---

## Troubleshooting

### Common Issues

#### Issue: "Python not found"
**Solution:**
```bash
# Verify Python installation
python --version

# If not installed, download from python.org
# Ensure Python 3.9+ is installed
```

#### Issue: "Module not found" errors
**Solution:**
```bash
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "Port 8080 already in use"
**Solution:**
```bash
# Option 1: Use a different port
python -m http.server 8081

# Option 2: Kill process using port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

#### Issue: Dashboard shows no data
**Solution:**
- Ensure AI models are running
- Check browser console for errors (F12)
- Verify network connectivity
- Check if models are outputting data

#### Issue: Terraform deployment fails
**Solution:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Terraform version
terraform version

# Check for syntax errors
terraform validate

# Review detailed error logs
terraform apply -auto-approve
```

---

## System Architecture

When running locally, the system operates as follows:

```
┌─────────────────────────────────────────┐
│         Browser (localhost:8080)        │
│              Dashboard UI               │
└─────────────────────────────────────────┘
                    ▲
                    │ HTTP
                    ▼
┌─────────────────────────────────────────┐
│        Python HTTP Server (8080)        │
│         Serves Static Files             │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      Anomaly Detection Model            │
│      (Isolation Forest)                 │
│      - Monitors system metrics          │
│      - Detects anomalies                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│    Degradation Predictor Model          │
│    (Time Series Forecasting)            │
│    - Predicts failures                  │
│    - Calculates risk scores             │
└─────────────────────────────────────────┘
```

---

## Performance Metrics

### Expected Performance
- **Dashboard Load Time:** < 2 seconds
- **AI Model Response:** < 100ms per prediction
- **Anomaly Detection Rate:** > 95% accuracy
- **False Positive Rate:** < 5%

### Monitoring
- Check browser DevTools (F12) for performance metrics
- Monitor Python console output for model performance
- Review system resource usage (CPU, Memory)

---

## Next Steps

After running the system locally:

1. **Explore the Dashboard**
   - Navigate through different sections
   - Trigger test disaster scenarios
   - Review AI predictions

2. **Test Disaster Scenarios**
   - Use the disaster simulator
   - Observe automated recovery
   - Analyze RTO/RPO metrics

3. **Deploy to Cloud**
   - Follow cloud deployment steps
   - Configure multi-region setup
   - Enable real-time monitoring

4. **Customize and Extend**
   - Add custom disaster scenarios
   - Tune AI model parameters
   - Integrate with existing systems

---

## Support and Documentation

- **Full Documentation:** See `docs/` directory
- **Architecture Details:** `docs/architecture.md`
- **API Reference:** `docs/api-reference.md`
- **Research Paper:** Shi et al. (2020) - See README.md

---

## Quick Reference Commands

```bash
# Start everything (automated)
.\run-local.ps1

# Quick dashboard only
quick-start.bat

# Manual dashboard
cd dashboard\frontend && python -m http.server 8080

# Run AI models
.\venv\Scripts\activate
python ai-models\anomaly-detection\isolation-forest\detector.py
python ai-models\prediction\degradation-predictor\predictor.py

# Deploy to cloud
cd infrastructure\terraform && terraform apply
```

---

**Last Updated:** January 2026
**Version:** 1.0.0
