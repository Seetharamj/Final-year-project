"""
Dashboard Backend API Server
Provides real-time data and WebSocket connections for the disaster recovery dashboard
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import json
import random
from datetime import datetime
from typing import List, Dict
import uvicorn

app = FastAPI(title="Disaster Recovery Dashboard API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending message: {e}")

manager = ConnectionManager()


def get_system_metrics():
    """Generate system metrics data"""
    return {
        "riskScore": random.randint(10, 30),
        "regions": [
            {
                "id": "us-east-1",
                "name": "US East 1",
                "role": "Primary",
                "status": "active",
                "uptime": round(99.98 + random.random() * 0.02, 2),
                "latency": random.randint(40, 60),
                "load": random.randint(60, 80),
                "instances": 24,
                "databases": 8
            },
            {
                "id": "us-west-2",
                "name": "US West 2",
                "role": "Secondary",
                "status": "standby",
                "uptime": round(99.96 + random.random() * 0.02, 2),
                "latency": random.randint(45, 65),
                "load": random.randint(20, 40),
                "instances": 12,
                "databases": 4
            },
            {
                "id": "eu-west-1",
                "name": "EU West 1",
                "role": "DR Site",
                "status": "cold",
                "uptime": 100.0,
                "latency": random.randint(90, 110),
                "load": random.randint(3, 10),
                "instances": 4,
                "databases": 2
            }
        ],
        "ai": {
            "anomalies": random.randint(0, 2),
            "degradationProbability": round(random.random() * 0.05, 4),
            "detectionAccuracy": round(0.96 + random.random() * 0.02, 3),
            "predictionConfidence": round(0.93 + random.random() * 0.04, 3),
            "rto": round(2.0 + random.random() * 1.0, 1),
            "rpo": round(0.3 + random.random() * 0.4, 1)
        },
        "components": {
            "hazards": {
                "active": random.randint(2, 5),
                "percentage": random.randint(15, 25)
            },
            "environment": {
                "regions": 3,
                "percentage": 100
            },
            "exposure": {
                "assets": random.randint(1200, 1300),
                "percentage": random.randint(60, 70)
            },
            "vulnerability": {
                "level": "Minimal",
                "percentage": random.randint(10, 20)
            },
            "recovery": {
                "level": "Excellent",
                "percentage": random.randint(90, 98)
            }
        },
        "recovery": {
            "availability": round(99.98 + random.random() * 0.02, 2),
            "backupSuccessRate": 100,
            "recoveryTests": {"passed": 24, "total": 24},
            "complianceScore": random.randint(96, 99)
        }
    }


def get_hazard_details():
    """Get detailed information about hazards"""
    hazards = [
        {
            "id": "haz-001",
            "type": "Network Latency Spike",
            "severity": "Low",
            "region": "us-east-1",
            "probability": "0.12%",
            "impact": "Minimal service degradation",
            "mitigation": "Auto-scaling enabled, load balancer configured",
            "status": "Monitored",
            "detectedAt": datetime.now().isoformat(),
            "metrics": {
                "currentLatency": "52ms",
                "normalLatency": "45ms",
                "threshold": "100ms"
            }
        },
        {
            "id": "haz-002",
            "type": "Database Connection Pool",
            "severity": "Low",
            "region": "us-west-2",
            "probability": "0.08%",
            "impact": "Potential connection delays",
            "mitigation": "Connection pool auto-expansion configured",
            "status": "Monitored",
            "detectedAt": datetime.now().isoformat(),
            "metrics": {
                "activeConnections": "67",
                "maxConnections": "100",
                "threshold": "90"
            }
        },
        {
            "id": "haz-003",
            "type": "Storage Capacity",
            "severity": "Very Low",
            "region": "eu-west-1",
            "probability": "0.03%",
            "impact": "None - within normal range",
            "mitigation": "Auto-scaling storage enabled",
            "status": "Normal",
            "detectedAt": datetime.now().isoformat(),
            "metrics": {
                "usedStorage": "68%",
                "availableStorage": "32%",
                "threshold": "85%"
            }
        }
    ]
    return hazards


def get_region_details(region_id: str):
    """Get detailed information about a specific region"""
    regions_data = {
        "us-east-1": {
            "id": "us-east-1",
            "name": "US East (N. Virginia)",
            "role": "Primary",
            "status": "active",
            "location": {
                "country": "United States",
                "city": "Ashburn, Virginia",
                "coordinates": {"lat": 39.0438, "lon": -77.4874}
            },
            "infrastructure": {
                "ec2Instances": 24,
                "databases": 8,
                "loadBalancers": 3,
                "storageGB": 5120
            },
            "metrics": {
                "uptime": 99.99,
                "latency": 45,
                "load": 67,
                "cpu": 45,
                "memory": 62,
                "network": 234
            },
            "services": [
                {"name": "Web Servers", "status": "healthy", "count": 12},
                {"name": "Application Servers", "status": "healthy", "count": 8},
                {"name": "Database Servers", "status": "healthy", "count": 4}
            ],
            "recentEvents": [
                {
                    "type": "info",
                    "message": "Auto-scaling triggered: Added 2 instances",
                    "timestamp": "5 minutes ago"
                },
                {
                    "type": "success",
                    "message": "Backup completed successfully",
                    "timestamp": "15 minutes ago"
                }
            ]
        },
        "us-west-2": {
            "id": "us-west-2",
            "name": "US West (Oregon)",
            "role": "Secondary",
            "status": "standby",
            "location": {
                "country": "United States",
                "city": "Boardman, Oregon",
                "coordinates": {"lat": 45.8399, "lon": -119.7006}
            },
            "infrastructure": {
                "ec2Instances": 12,
                "databases": 4,
                "loadBalancers": 2,
                "storageGB": 2560
            },
            "metrics": {
                "uptime": 99.98,
                "latency": 52,
                "load": 23,
                "cpu": 28,
                "memory": 41,
                "network": 156
            },
            "services": [
                {"name": "Web Servers", "status": "healthy", "count": 6},
                {"name": "Application Servers", "status": "healthy", "count": 4},
                {"name": "Database Servers", "status": "healthy", "count": 2}
            ],
            "recentEvents": [
                {
                    "type": "info",
                    "message": "Standby mode - ready for failover",
                    "timestamp": "1 hour ago"
                }
            ]
        },
        "eu-west-1": {
            "id": "eu-west-1",
            "name": "EU West (Ireland)",
            "role": "DR Site",
            "status": "cold",
            "location": {
                "country": "Ireland",
                "city": "Dublin",
                "coordinates": {"lat": 53.3498, "lon": -6.2603}
            },
            "infrastructure": {
                "ec2Instances": 4,
                "databases": 2,
                "loadBalancers": 1,
                "storageGB": 1024
            },
            "metrics": {
                "uptime": 100.0,
                "latency": 98,
                "load": 5,
                "cpu": 12,
                "memory": 18,
                "network": 45
            },
            "services": [
                {"name": "Web Servers", "status": "standby", "count": 2},
                {"name": "Application Servers", "status": "standby", "count": 1},
                {"name": "Database Servers", "status": "standby", "count": 1}
            ],
            "recentEvents": [
                {
                    "type": "success",
                    "message": "DR site health check passed",
                    "timestamp": "30 minutes ago"
                }
            ]
        }
    }
    return regions_data.get(region_id, {})


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Disaster Recovery Dashboard API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "metrics": "/api/dashboard/latest",
            "hazards": "/api/hazards",
            "region": "/api/region/{region_id}",
            "websocket": "/ws"
        }
    }


@app.get("/api/dashboard/latest")
async def get_latest_data():
    """Get latest dashboard data"""
    metrics = get_system_metrics()
    return JSONResponse(content={
        "type": "metrics",
        "payload": metrics,
        "timestamp": datetime.now().isoformat()
    })


@app.get("/api/hazards")
async def get_hazards():
    """Get detailed hazard information"""
    hazards = get_hazard_details()
    return JSONResponse(content={
        "hazards": hazards,
        "total": len(hazards),
        "timestamp": datetime.now().isoformat()
    })


@app.get("/api/region/{region_id}")
async def get_region(region_id: str):
    """Get detailed information about a specific region"""
    region_data = get_region_details(region_id)
    if not region_data:
        return JSONResponse(
            status_code=404,
            content={"error": f"Region {region_id} not found"}
        )
    return JSONResponse(content=region_data)


@app.get("/api/components/{component_type}")
async def get_component_details(component_type: str):
    """Get detailed information about disaster system components"""
    components_info = {
        "hazards": {
            "type": "Hazards",
            "description": "Potential threats and risk factors affecting system stability",
            "details": get_hazard_details(),
            "totalActive": 3,
            "severity": "Low",
            "monitoring": "Active 24/7 monitoring with AI-powered detection"
        },
        "environment": {
            "type": "Environment",
            "description": "Multi-region cloud infrastructure deployment",
            "regions": [
                {"name": "US East 1", "status": "Active", "role": "Primary"},
                {"name": "US West 2", "status": "Standby", "role": "Secondary"},
                {"name": "EU West 1", "status": "Cold Standby", "role": "DR Site"}
            ],
            "coverage": "Global",
            "redundancy": "Triple redundancy across continents"
        },
        "exposure": {
            "type": "Exposure",
            "description": "Assets and resources at risk",
            "assets": {
                "total": 1247,
                "critical": 342,
                "protected": 1247,
                "protectionRate": "100%"
            },
            "breakdown": [
                {"category": "EC2 Instances", "count": 40},
                {"category": "Databases", "count": 14},
                {"category": "Storage Volumes", "count": 156},
                {"category": "Network Resources", "count": 89},
                {"category": "Other Services", "count": 948}
            ]
        },
        "vulnerability": {
            "type": "Vulnerability",
            "description": "System weaknesses and security posture",
            "score": "Minimal",
            "details": {
                "securityScore": 95,
                "patchLevel": "Up to date",
                "knownVulnerabilities": 0,
                "lastAssessment": "2 hours ago"
            },
            "mitigations": [
                "Multi-factor authentication enabled",
                "Encryption at rest and in transit",
                "Regular security audits",
                "Automated patch management"
            ]
        },
        "recovery": {
            "type": "Recovery",
            "description": "Disaster recovery capabilities and readiness",
            "score": "Excellent",
            "metrics": {
                "rto": "2.3 minutes",
                "rpo": "0.5 minutes",
                "backupFrequency": "Every 5 minutes",
                "lastTest": "24 hours ago",
                "testSuccessRate": "100%"
            },
            "capabilities": [
                "Automated failover",
                "Cross-region replication",
                "Point-in-time recovery",
                "Automated backup verification"
            ]
        }
    }
    
    component_data = components_info.get(component_type.lower())
    if not component_data:
        return JSONResponse(
            status_code=404,
            content={"error": f"Component type '{component_type}' not found"}
        )
    
    return JSONResponse(content=component_data)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial data
        initial_data = {
            "type": "connection",
            "payload": {"status": "connected", "message": "Real-time updates enabled"},
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_json(initial_data)
        
        # Keep connection alive and send periodic updates
        while True:
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
            # Send metrics update
            metrics = get_system_metrics()
            update = {
                "type": "metrics",
                "payload": metrics,
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send_json(update)
            
            # Randomly send anomaly alerts (10% chance)
            if random.random() < 0.1:
                anomaly = {
                    "type": "anomaly",
                    "payload": {
                        "severity": random.choice(["Low", "Medium"]),
                        "affected_metrics": [random.choice(["CPU", "Memory", "Network", "Latency"])],
                        "timestamp": datetime.now().isoformat(),
                        "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"])
                    },
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(anomaly)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "activeConnections": len(manager.active_connections)
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Starting Disaster Recovery Dashboard API Server")
    print("=" * 60)
    print(f"Dashboard API: http://localhost:5000")
    print(f"WebSocket: ws://localhost:5000/ws")
    print(f"API Docs: http://localhost:5000/docs")
    print(f"Health Check: http://localhost:5000/health")
    print("=" * 60)
    print("Server is ready to accept connections")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
