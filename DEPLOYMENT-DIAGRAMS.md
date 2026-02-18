# EC2 Deployment Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          LOCAL MACHINE (Windows)                         │
│                                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐   │
│  │   AWS        │   │  Download    │   │  Configure Security      │   │
│  │   Console    │ → │  Key Pair    │ → │  Groups (22, 80, 8080)   │   │
│  │              │   │  (.pem)      │   │                          │   │
│  └──────────────┘   └──────────────┘   └──────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SSH Connection
                                    │ ssh -i "key.pem" ubuntu@EC2-IP
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EC2 INSTANCE (Ubuntu 22.04)                         │
│                                                                          │
│  Step 1: System Setup                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  sudo apt update && sudo apt upgrade -y                         │   │
│  │  sudo apt install python3 python3-pip python3-venv git          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  Step 2: Clone Project                                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  cd ~                                                            │   │
│  │  git clone https://github.com/YOUR-REPO/project.git project-1   │   │
│  │  cd project-1                                                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  Step 3: Setup Environment                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  python3 -m venv venv                                            │   │
│  │  source venv/bin/activate                                        │   │
│  │  pip install -r requirements.txt                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                                    ▼                                     │
│  Step 4: Start Services                                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  chmod +x start-ec2.sh                                           │   │
│  │  ./start-ec2.sh                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RUNNING SERVICES                                 │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────┐ │
│  │  Anomaly Detection   │  │  Degradation         │  │  Dashboard   │ │
│  │  Model               │  │  Predictor           │  │  (Port 8080) │ │
│  │                      │  │                      │  │              │ │
│  │  detector.py         │  │  predictor.py        │  │  http.server │ │
│  │  [Background]        │  │  [Background]        │  │  [Running]   │ │
│  │                      │  │                      │  │              │ │
│  │  📊 Monitors metrics │  │  🔮 Predicts issues  │  │  🖥️  Web UI  │ │
│  │  📝 logs/anomaly.log │  │  📝 logs/predictor   │  │  📝 logs/    │ │
│  │                      │  │     .log             │  │     dashboard│ │
│  │                      │  │                      │  │     .log     │ │
│  └──────────────────────┘  └──────────────────────┘  └──────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ HTTP Request
                                     │ http://EC2-PUBLIC-IP:8080
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER'S WEB BROWSER                              │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  🌐 Disaster Recovery Dashboard                                   │ │
│  │                                                                    │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │ │
│  │  │ System      │  │ Anomaly     │  │ Predictions │              │ │
│  │  │ Status      │  │ Detection   │  │ & Alerts    │              │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │ │
│  │                                                                    │ │
│  │  Real-time monitoring and disaster recovery management            │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Region Deployment Architecture

```
                         ┌─────────────────────────┐
                         │   Route 53 / Load       │
                         │   Balancer              │
                         │   (Traffic Distribution)│
                         └───────────┬─────────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
                 ▼                   ▼                   ▼
    ┌────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
    │   us-east-1        │ │   us-west-2        │ │   eu-west-1        │
    │   (N. Virginia)    │ │   (Oregon)         │ │   (Ireland)        │
    │                    │ │                    │ │                    │
    │  ┌──────────────┐  │ │  ┌──────────────┐  │ │  ┌──────────────┐  │
    │  │ EC2 Instance │  │ │  │ EC2 Instance │  │ │  │ EC2 Instance │  │
    │  │              │  │ │  │              │  │ │  │              │  │
    │  │ • Dashboard  │  │ │  │ • Dashboard  │  │ │  │ • Dashboard  │  │
    │  │ • AI Models  │  │ │  │ • AI Models  │  │ │  │ • AI Models  │  │
    │  │ • Monitoring │  │ │  │ • Monitoring │  │ │  │ • Monitoring │  │
    │  └──────────────┘  │ │  └──────────────┘  │ │  └──────────────┘  │
    │                    │ │                    │ │                    │
    │  ┌──────────────┐  │ │  ┌──────────────┐  │ │  ┌──────────────┐  │
    │  │ S3 Bucket    │  │ │  │ S3 Bucket    │  │ │  │ S3 Bucket    │  │
    │  │ (Backups)    │  │ │  │ (Backups)    │  │ │  │ (Backups)    │  │
    │  └──────────────┘  │ │  └──────────────┘  │ │  └──────────────┘  │
    │         │          │ │         │          │ │         │          │
    └─────────┼──────────┘ └─────────┼──────────┘ └─────────┼──────────┘
              │                      │                      │
              └──────────────────────┴──────────────────────┘
                     Cross-Region Replication
```

---

## Service Communication Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EC2 Instance                                  │
│                                                                      │
│  ┌────────────────┐                                                 │
│  │  CloudWatch    │ ← Metrics ─────────────┐                        │
│  │  Monitoring    │                        │                        │
│  └────────────────┘                        │                        │
│                                             │                        │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Anomaly Detection Model (detector.py)                      │    │
│  │  • Monitors system metrics                                  │    │
│  │  • Detects unusual patterns                                 │    │
│  │  • Triggers alerts                                          │    │
│  └────────────────┬───────────────────────────────────────────┘    │
│                   │ Anomaly Data                                    │
│                   ▼                                                 │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Degradation Predictor (predictor.py)                       │    │
│  │  • Analyzes trends                                          │    │
│  │  • Predicts failures                                        │    │
│  │  • Calculates RTO/RPO                                       │    │
│  └────────────────┬───────────────────────────────────────────┘    │
│                   │ Prediction Data                                 │
│                   ▼                                                 │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  Dashboard (http.server:8080)                               │    │
│  │  • Displays real-time data                                  │    │
│  │  • Shows alerts                                             │    │
│  │  • Provides control interface                               │    │
│  └────────────────┬───────────────────────────────────────────┘    │
│                   │                                                 │
└───────────────────┼─────────────────────────────────────────────────┘
                    │
                    ▼
              User Browser
```

---

## File Structure on EC2

```
/home/ubuntu/
│
└── project-1/
    ├── venv/                          # Python virtual environment
    │   ├── bin/
    │   ├── lib/
    │   └── ...
    │
    ├── ai-models/                     # AI/ML models
    │   ├── anomaly-detection/
    │   │   └── isolation-forest/
    │   │       └── detector.py        # Anomaly detection service
    │   └── prediction/
    │       └── degradation-predictor/
    │           └── predictor.py       # Degradation prediction service
    │
    ├── dashboard/                     # Web dashboard
    │   └── frontend/
    │       ├── index.html
    │       ├── css/
    │       └── js/
    │
    ├── infrastructure/                # Infrastructure as Code
    │   └── terraform/
    │       ├── main.tf
    │       └── variables.tf
    │
    ├── logs/                          # Service logs
    │   ├── anomaly-detector.log
    │   ├── degradation-predictor.log
    │   └── dashboard.log
    │
    ├── requirements.txt               # Python dependencies
    ├── setup-ec2.sh                   # Initial setup script
    ├── start-ec2.sh                   # Service startup script
    │
    └── README.md                      # Project documentation
```

---

## Security Group Configuration

```
┌─────────────────────────────────────────────────────────────┐
│  Security Group: disaster-recovery-sg                        │
│                                                              │
│  Inbound Rules:                                              │
│  ┌────────┬──────┬─────────────┬──────────────────────┐    │
│  │ Type   │ Port │ Protocol    │ Source               │    │
│  ├────────┼──────┼─────────────┼──────────────────────┤    │
│  │ SSH    │ 22   │ TCP         │ Your IP / 0.0.0.0/0  │    │
│  │ HTTP   │ 80   │ TCP         │ 0.0.0.0/0            │    │
│  │ Custom │ 8080 │ TCP         │ 0.0.0.0/0            │    │
│  │ Custom │ 5000 │ TCP         │ 0.0.0.0/0            │    │
│  └────────┴──────┴─────────────┴──────────────────────┘    │
│                                                              │
│  Outbound Rules:                                             │
│  ┌────────┬──────┬─────────────┬──────────────────────┐    │
│  │ Type   │ Port │ Protocol    │ Destination          │    │
│  ├────────┼──────┼─────────────┼──────────────────────┤    │
│  │ All    │ All  │ All         │ 0.0.0.0/0            │    │
│  └────────┴──────┴─────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Timeline

```
Time    Activity                                    Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0:00    Create EC2 instance                         ⏳ 2-3 min
0:03    Download key pair                           ✅ Instant
0:03    Configure security groups                   ✅ Instant
0:03    Wait for instance to be running             ⏳ 1-2 min
0:05    SSH connect to instance                     ✅ Instant
0:05    Update system (apt update/upgrade)          ⏳ 3-5 min
0:10    Install Python, Git, tools                  ⏳ 2-3 min
0:13    Clone project from Git                      ⏳ 1-2 min
0:15    Create virtual environment                  ⏳ 1 min
0:16    Install dependencies (pip install)          ⏳ 5-10 min
0:26    Make scripts executable                     ✅ Instant
0:26    Run start-ec2.sh                            ⏳ 30 sec
0:27    Verify services running                     ✅ Instant
0:27    Access dashboard in browser                 ✅ Done!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Time: ~25-30 minutes
```

---

## Resource Usage

```
┌─────────────────────────────────────────────────────────────┐
│  EC2 Instance: t2.medium                                     │
│                                                              │
│  CPU Usage:                                                  │
│  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20-30%    │
│                                                              │
│  Memory Usage:                                               │
│  ████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░  50-60%    │
│                                                              │
│  Disk Usage:                                                 │
│  ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  15-20%    │
│                                                              │
│  Network:                                                    │
│  In:  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Low        │
│  Out: ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  Moderate   │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** February 2026  
**Version:** 1.0.0
