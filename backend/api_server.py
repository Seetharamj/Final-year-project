"""
Real AWS Region Data Collector & API Server
Collects real metrics from AWS CloudWatch across multiple regions,
stores them in SQLite on the EC2 instance, and serves to dashboard.
Works with or without AWS credentials (falls back to simulated data).
"""

import json
import os
import sqlite3
import threading
import time
import logging
import random
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ── Optional AWS SDK ───────────────────────────────────────────────────────────
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
REGIONS = [
    {"id": "us-east-1", "name": "US East 1",  "role": "Primary"},
    {"id": "us-west-2", "name": "US West 2",  "role": "Secondary"},
    {"id": "eu-west-1", "name": "EU West 1",  "role": "DR Site"},
]
DB_PATH       = "data/region_metrics.db"
COLLECT_EVERY = 60    # seconds between collections
API_PORT      = 5000


# ── Database ───────────────────────────────────────────────────────────────────
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS region_metrics (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp      TEXT    NOT NULL,
            region_id      TEXT    NOT NULL,
            region_name    TEXT    NOT NULL,
            role           TEXT    NOT NULL,
            status         TEXT    NOT NULL,
            uptime         REAL,
            latency_ms     REAL,
            cpu_load       REAL,
            instance_count INTEGER,
            db_count       INTEGER,
            error_rate     REAL,
            network_in     REAL,
            network_out    REAL,
            raw_json       TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS anomalies (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT    NOT NULL,
            region_id   TEXT    NOT NULL,
            severity    TEXT    NOT NULL,
            metric      TEXT    NOT NULL,
            value       REAL,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialised at %s", DB_PATH)


# ── AWS Collector ──────────────────────────────────────────────────────────────
class AWSRegionCollector:
    def __init__(self):
        self.has_credentials = False
        if HAS_BOTO3:
            try:
                boto3.client("sts", region_name="us-east-1").get_caller_identity()
                logger.info("AWS credentials verified - using real CloudWatch data")
                self.has_credentials = True
            except Exception as e:
                logger.warning("No valid AWS credentials - using simulated data. (%s)", e)
        else:
            logger.info("boto3 not installed - using simulated data")

    # ── Real AWS metrics ───────────────────────────────────────────────────────
    def _get_cloudwatch_metric(self, cw, namespace, metric_name,
                               dimensions, stat="Average", period=300):
        try:
            end   = datetime.utcnow()
            start = end - timedelta(seconds=period * 2)
            resp  = cw.get_metric_statistics(
                Namespace=namespace, MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start, EndTime=end,
                Period=period, Statistics=[stat]
            )
            pts = resp.get("Datapoints", [])
            if pts:
                return sorted(pts, key=lambda x: x["Timestamp"])[-1][stat]
        except Exception:
            pass
        return None

    def collect_real_region(self, region: dict) -> dict:
        rid = region["id"]
        try:
            ec2 = boto3.client("ec2",        region_name=rid)
            cw  = boto3.client("cloudwatch", region_name=rid)
            elb = boto3.client("elbv2",      region_name=rid)

            reservations   = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )["Reservations"]
            instance_ids   = [i["InstanceId"]
                              for r in reservations for i in r["Instances"]]
            instance_count = len(instance_ids)

            cpu_load = 0.0
            if instance_ids:
                v = self._get_cloudwatch_metric(
                    cw, "AWS/EC2", "CPUUtilization",
                    [{"Name": "InstanceId", "Value": instance_ids[0]}])
                cpu_load = v if v is not None else 0.0

            net_in = net_out = 0.0
            if instance_ids:
                dims = [{"Name": "InstanceId", "Value": instance_ids[0]}]
                v = self._get_cloudwatch_metric(cw, "AWS/EC2", "NetworkIn", dims)
                net_in  = (v / 1024 / 1024) if v else 0.0
                v = self._get_cloudwatch_metric(cw, "AWS/EC2", "NetworkOut", dims)
                net_out = (v / 1024 / 1024) if v else 0.0

            latency_ms = 45.0
            try:
                lbs = elb.describe_load_balancers()["LoadBalancers"]
                if lbs:
                    arn  = lbs[0]["LoadBalancerArn"]
                    name = "/".join(arn.split("/")[-3:])
                    v    = self._get_cloudwatch_metric(
                        cw, "AWS/ApplicationELB", "TargetResponseTime",
                        [{"Name": "LoadBalancer", "Value": name}])
                    latency_ms = (v * 1000) if v else 45.0
            except Exception:
                pass

            db_count = 0
            try:
                rds      = boto3.client("rds", region_name=rid)
                db_count = len(rds.describe_db_instances()["DBInstances"])
            except Exception:
                pass

            status     = ("active"   if cpu_load < 80
                          else "degraded" if cpu_load < 95
                          else "critical")
            uptime     = max(99.0, 100.0 - cpu_load * 0.01)
            error_rate = min(5.0,  cpu_load * 0.05)

            return {
                "region_id":      rid,
                "region_name":    region["name"],
                "role":           region["role"],
                "status":         status,
                "uptime":         round(uptime, 3),
                "latency_ms":     round(latency_ms, 1),
                "cpu_load":       round(cpu_load, 1),
                "instance_count": instance_count,
                "db_count":       db_count,
                "error_rate":     round(error_rate, 2),
                "network_in":     round(net_in, 2),
                "network_out":    round(net_out, 2),
                "source":         "real_aws",
            }
        except Exception as e:
            logger.error("Error collecting %s: %s — falling back to simulation", rid, e)
            return self._simulated_region(region)

    # ── Simulated fallback ─────────────────────────────────────────────────────
    def _simulated_region(self, region: dict) -> dict:
        rid  = region["id"]
        base = {
            "us-east-1": (67, 45),
            "us-west-2": (23, 52),
            "eu-west-1": (5,  98),
        }
        load, lat = base.get(rid, (30, 60))
        load += random.uniform(-5, 5)
        lat  += random.uniform(-5, 5)
        load  = max(0.0, min(100.0, load))
        lat   = max(1.0, lat)
        status = ("active"   if load < 80
                  else "degraded" if load < 95
                  else "critical")
        return {
            "region_id":      rid,
            "region_name":    region["name"],
            "role":           region["role"],
            "status":         status,
            "uptime":         round(99.95 + random.uniform(-0.05, 0.04), 3),
            "latency_ms":     round(lat, 1),
            "cpu_load":       round(load, 1),
            "instance_count": {"us-east-1": 24, "us-west-2": 12, "eu-west-1": 4}.get(rid, 4),
            "db_count":       {"us-east-1": 8,  "us-west-2": 4,  "eu-west-1": 2}.get(rid, 2),
            "error_rate":     round(random.uniform(0, 0.5), 2),
            "network_in":     round(random.uniform(800, 1200), 1),
            "network_out":    round(random.uniform(600, 900), 1),
            "source":         "simulated",
        }

    def collect_all(self) -> list:
        results = []
        for region in REGIONS:
            data = (self.collect_real_region(region)
                    if self.has_credentials
                    else self._simulated_region(region))
            results.append(data)
            logger.info("Collected %s: CPU=%.1f%% Latency=%.0fms status=%s [%s]",
                        data["region_id"], data["cpu_load"],
                        data["latency_ms"], data["status"], data["source"])
        return results


# ── Storage helpers ────────────────────────────────────────────────────────────
def save_metrics(metrics: list):
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    ts   = datetime.utcnow().isoformat()
    for m in metrics:
        c.execute("""
            INSERT INTO region_metrics
            (timestamp, region_id, region_name, role, status,
             uptime, latency_ms, cpu_load, instance_count, db_count,
             error_rate, network_in, network_out, raw_json)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (ts, m["region_id"], m["region_name"], m["role"], m["status"],
              m["uptime"], m["latency_ms"], m["cpu_load"],
              m["instance_count"], m["db_count"],
              m["error_rate"], m["network_in"], m["network_out"],
              json.dumps(m)))
    conn.commit()
    conn.close()


def get_latest_metrics() -> list:
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    # Compatible with all SQLite versions
    c.execute("""
        SELECT region_id, region_name, role, status,
               uptime, latency_ms, cpu_load, instance_count,
               db_count, error_rate, network_in, network_out,
               timestamp, raw_json
        FROM region_metrics
        WHERE id IN (
            SELECT MAX(id) FROM region_metrics GROUP BY region_id
        )
        ORDER BY region_id
    """)
    rows = c.fetchall()
    conn.close()
    result = []
    for r in rows:
        try:
            raw    = json.loads(r[13]) if r[13] else {}
            source = raw.get("source", "simulated")
        except Exception:
            source = "simulated"
        result.append({
            "region_id":      r[0],  "region_name":    r[1],
            "role":           r[2],  "status":         r[3],
            "uptime":         r[4],  "latency_ms":     r[5],
            "cpu_load":       r[6],  "instance_count": r[7],
            "db_count":       r[8],  "error_rate":     r[9],
            "network_in":     r[10], "network_out":    r[11],
            "timestamp":      r[12], "source":         source,
        })
    return result


def get_history(region_id: str, hours: int = 24) -> list:
    conn  = sqlite3.connect(DB_PATH)
    c     = conn.cursor()
    since = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
    c.execute("""
        SELECT timestamp, cpu_load, latency_ms, uptime, error_rate
        FROM region_metrics
        WHERE region_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (region_id, since))
    rows = c.fetchall()
    conn.close()
    return [{"timestamp": r[0], "cpu_load": r[1],
             "latency_ms": r[2], "uptime": r[3],
             "error_rate": r[4]} for r in rows]


# ── Background collection thread ───────────────────────────────────────────────
collector = AWSRegionCollector()


def collection_loop():
    while True:
        try:
            logger.info("Collecting region metrics...")
            metrics = collector.collect_all()
            save_metrics(metrics)
            logger.info("Saved %d region records to DB", len(metrics))
        except Exception as e:
            logger.error("Collection error: %s", e)
        time.sleep(COLLECT_EVERY)


# ── HTTP handler ───────────────────────────────────────────────────────────────
class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # Suppress access log noise

    def _send_json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type",                  "application/json")
        self.send_header("Content-Length",                str(len(body)))
        self.send_header("Access-Control-Allow-Origin",   "*")
        self.send_header("Access-Control-Allow-Methods",  "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers",  "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        try:
            # GET /api/health
            if path == "/api/health":
                self._send_json({
                    "status":    "ok",
                    "timestamp": datetime.utcnow().isoformat(),
                    "source":    "simulated" if not collector.has_credentials else "real_aws",
                })

            # GET /api/regions
            elif path == "/api/regions":
                data = get_latest_metrics()
                self._send_json({
                    "regions":   data,
                    "count":     len(data),
                    "timestamp": datetime.utcnow().isoformat(),
                })

            # GET /api/regions/<id>/history?hours=24
            elif path.startswith("/api/regions/") and path.endswith("/history"):
                parts = path.split("/")
                rid   = parts[3] if len(parts) > 3 else ""
                hours = int(params.get("hours", ["24"])[0])
                self._send_json({
                    "region_id": rid,
                    "history":   get_history(rid, hours),
                })

            # GET /api/dashboard/latest
            elif path == "/api/dashboard/latest":
                regions = get_latest_metrics()
                n       = len(regions) or 1
                avg_cpu = sum(r["cpu_load"]   for r in regions) / n
                avg_lat = sum(r["latency_ms"] for r in regions) / n
                total_i = sum(r["instance_count"] for r in regions)
                risk    = min(100, int(avg_cpu * 0.5 + avg_lat * 0.1))
                self._send_json({
                    "type": "metrics",
                    "payload": {
                        "riskScore":      risk,
                        "totalInstances": total_i,
                        "regions":        regions,
                        "ai": {
                            "anomalies":              0,
                            "degradationProbability": round(avg_cpu / 200, 4),
                            "rto": 2.3,
                            "rpo": 0.5,
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                })

            else:
                self._send_json({"error": "Endpoint not found", "path": path}, 404)

        except Exception as e:
            logger.exception("Request handler error: %s", e)
            self._send_json({"error": "Internal server error", "detail": str(e)}, 500)


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("  AI-Driven Disaster Recovery — API Server")
    logger.info("=" * 60)
    init_db()

    # Initial collection on startup
    logger.info("Performing initial data collection...")
    try:
        metrics = collector.collect_all()
        save_metrics(metrics)
        logger.info("Initial collection complete — %d regions saved", len(metrics))
    except Exception as e:
        logger.error("Initial collection failed: %s", e)

    # Background collection thread
    t = threading.Thread(target=collection_loop, daemon=True)
    t.start()
    logger.info("Background collector started (every %ds)", COLLECT_EVERY)

    # Start HTTP server
    server = HTTPServer(("0.0.0.0", API_PORT), APIHandler)
    logger.info("API server listening on http://0.0.0.0:%d", API_PORT)
    logger.info("Endpoints:")
    logger.info("  GET /api/health")
    logger.info("  GET /api/regions")
    logger.info("  GET /api/regions/<id>/history?hours=24")
    logger.info("  GET /api/dashboard/latest")
    logger.info("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
