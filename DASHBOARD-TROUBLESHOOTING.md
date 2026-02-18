# Dashboard Troubleshooting Guide

## Current Status

I've fixed the backend server crash (emoji encoding issue) and restarted it. Here's what should be running:

### Running Services:
1. **Backend API Server** - Port 5000
2. **Frontend Dashboard** - Port 8080

## Quick Test Steps

### Step 1: Verify Backend is Running

Open PowerShell and run:
```powershell
curl http://localhost:5000/health
```

**Expected output:**
```json
{"status":"healthy","timestamp":"...","activeConnections":0}
```

If you get an error, the backend isn't running. Start it with:
```powershell
python dashboard\backend\api_server.py
```

### Step 2: Verify Frontend is Running

Open PowerShell and run:
```powershell
curl http://localhost:8080
```

**Expected output:** HTML content starting with `<!DOCTYPE html>`

If you get an error, the frontend isn't running. Start it with:
```powershell
cd dashboard\frontend
python -m http.server 8080
```

### Step 3: Open Dashboard in Browser

1. Open your web browser (Chrome, Firefox, Edge)
2. Go to: **http://localhost:8080**
3. You should see the "Disaster Recovery Command Center" dashboard

### Step 4: Test Interactivity

1. **Open Browser Console** (Press F12)
2. Look for any errors in the Console tab
3. **Click on a card** (e.g., "Hazards" or "US East 1")
4. A modal popup should appear with detailed information

## Common Issues & Solutions

### Issue 1: "This site can't be reached" or "Connection refused"

**Problem:** Servers aren't running

**Solution:**
```powershell
# Terminal 1 - Start Backend
cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1
python dashboard\backend\api_server.py

# Terminal 2 - Start Frontend (open new terminal)
cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\dashboard\frontend
python -m http.server 8080
```

### Issue 2: Dashboard loads but clicking cards does nothing

**Problem:** JavaScript errors or backend not accessible

**Solution:**
1. Press F12 to open browser console
2. Look for errors (usually red text)
3. Common errors:
   - "Failed to fetch" → Backend server not running on port 5000
   - "WebSocket connection failed" → Backend server not running
   - "CORS error" → Backend CORS issue (already fixed in code)

### Issue 3: "Unable to fetch component details" notification

**Problem:** Backend API not responding

**Solution:**
1. Check if backend is running: `curl http://localhost:5000/health`
2. If not, restart backend: `python dashboard\backend\api_server.py`
3. Refresh the dashboard page

### Issue 4: Port already in use

**Problem:** Another process is using port 5000 or 8080

**Solution:**
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Find what's using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use different ports:
# Backend on port 5001:
python dashboard\backend\api_server.py --port 5001

# Frontend on port 8081:
python -m http.server 8081
```

## Manual Startup (Recommended)

Instead of using the batch file, start servers manually in separate terminals:

### Terminal 1 (Backend):
```powershell
cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1
python dashboard\backend\api_server.py
```

**You should see:**
```
============================================================
Starting Disaster Recovery Dashboard API Server
============================================================
Dashboard API: http://localhost:5000
WebSocket: ws://localhost:5000/ws
API Docs: http://localhost:5000/docs
Health Check: http://localhost:5000/health
============================================================
Server is ready to accept connections
============================================================
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

### Terminal 2 (Frontend):
```powershell
cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\dashboard\frontend
python -m http.server 8080
```

**You should see:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### Browser:
Open: **http://localhost:8080**

## Testing the API Directly

You can test the API endpoints directly in your browser:

- http://localhost:5000 - API info
- http://localhost:5000/docs - Interactive API documentation (Swagger UI)
- http://localhost:5000/health - Health check
- http://localhost:5000/api/dashboard/latest - Latest metrics
- http://localhost:5000/api/hazards - Hazard details
- http://localhost:5000/api/region/us-east-1 - Region details

## What Should Happen When You Click a Card

### Example: Clicking "Hazards" Card

1. Click on the "Hazards" component card
2. Dashboard JavaScript sends request to: `http://localhost:5000/api/components/hazards`
3. Backend returns JSON data with hazard details
4. A modal popup appears showing:
   - Active hazards list
   - Severity levels
   - Affected regions
   - Impact assessment
   - Mitigation strategies

### Example: Clicking "US East 1" Region Card

1. Click on the "US East 1" region card
2. Dashboard JavaScript sends request to: `http://localhost:5000/api/region/us-east-1`
3. Backend returns JSON data with region details
4. A modal popup appears showing:
   - Location information
   - Infrastructure (EC2 instances, databases, load balancers, storage)
   - Current metrics (CPU, Memory, Network)
   - Running services status
   - Recent events

## Browser Console Debugging

Open browser console (F12) and check for:

### Good Signs (No Errors):
```
WebSocket connected to backend
```

### Bad Signs (Errors to Fix):
```
WebSocket error: ...
Failed to fetch ...
CORS error ...
```

## Still Not Working?

If nothing works, try this simple test:

1. **Stop all servers** (Ctrl+C in both terminals)
2. **Start backend only:**
   ```powershell
   cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1
   python dashboard\backend\api_server.py
   ```
3. **Test backend in browser:** http://localhost:5000
   - You should see JSON with API info
4. **Test API docs:** http://localhost:5000/docs
   - You should see interactive API documentation
5. **If backend works, start frontend:**
   ```powershell
   cd C:\Users\naksh\OneDrive\Desktop\Documents\nakshu\project-1\dashboard\frontend
   python -m http.server 8080
   ```
6. **Open dashboard:** http://localhost:8080

## Need More Help?

Share the following information:

1. **Backend terminal output** - Copy everything from the backend terminal
2. **Frontend terminal output** - Copy everything from the frontend terminal
3. **Browser console errors** - Press F12, go to Console tab, copy any red errors
4. **What happens when you click a card** - Describe exactly what you see

---

**Last Updated:** February 2026
