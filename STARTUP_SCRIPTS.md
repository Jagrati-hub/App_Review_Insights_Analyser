# Startup Scripts Guide

This project includes convenient batch scripts to start the application servers on Windows.

## Available Scripts

### 1. `start-all.bat` (Recommended)
Starts both backend and frontend servers automatically.

**Usage:**
```bash
start-all.bat
```

**What it does:**
- Opens a new window for the Flask backend (port 5000)
- Waits 3 seconds for backend initialization
- Opens a new window for the Next.js frontend (port 3000)
- Both servers run in separate command windows

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### 2. `start-backend.bat`
Starts only the Flask backend server.

**Usage:**
```bash
start-backend.bat
```

**What it does:**
- Activates Python virtual environment
- Starts Flask API on port 5000
- Shows API endpoints and configuration

### 3. `start-frontend.bat`
Starts only the Next.js frontend server.

**Usage:**
```bash
start-frontend.bat
```

**What it does:**
- Navigates to frontend directory
- Starts Next.js dev server on port 3000

## First Time Setup

Before using these scripts, make sure you've completed the setup:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your `GROQ_API_KEY`

4. **Run the application:**
   ```bash
   start-all.bat
   ```

## Stopping the Servers

To stop the servers:
- Press `Ctrl+C` in each command window
- Or simply close the command windows

## Troubleshooting

### Port Already in Use

**Problem:** Port 5000 or 3000 is already in use

**Solution:**
1. Find the process using the port:
   ```bash
   netstat -ano | findstr :5000
   netstat -ano | findstr :3000
   ```
2. Kill the process:
   ```bash
   taskkill /PID <process_id> /F
   ```

### Virtual Environment Not Found

**Problem:** `venv\Scripts\activate` not found

**Solution:**
1. Create virtual environment:
   ```bash
   python -m venv venv
   ```
2. Run the script again

### npm Not Found

**Problem:** `npm` command not recognized

**Solution:**
1. Install Node.js from https://nodejs.org/
2. Restart your terminal
3. Run the script again

## Manual Start (Alternative)

If the batch scripts don't work, you can start the servers manually:

**Terminal 1 (Backend):**
```bash
venv\Scripts\activate
python phase2/ui_controller.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

## Production Deployment

These scripts are for development only. For production:

**Backend:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 phase2.ui_controller:app
```

**Frontend:**
```bash
cd frontend
npm run build
npm start
```
