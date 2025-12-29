# Quick Start Script for Investment Recommendation App
# This script helps you start the app without timeouts

Write-Host "🚀 Investment Recommendation App - Quick Start" -ForegroundColor Cyan
Write-Host ""

# Check if backend is already running
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    $backendRunning = $true
    Write-Host "✅ Backend is already running!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend is not running. Starting it now..." -ForegroundColor Yellow
}

# Start backend if not running
if (-not $backendRunning) {
    Write-Host ""
    Write-Host "📡 Starting Backend API..." -ForegroundColor Cyan
    Write-Host "   This will open in a new window. Keep it running!" -ForegroundColor Yellow
    Write-Host ""
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
    
    Write-Host "⏳ Waiting for backend to start (10 seconds)..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Check if backend started successfully
    $retries = 0
    $maxRetries = 6
    while ($retries -lt $maxRetries) {
        try {
            $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            Write-Host "✅ Backend is ready!" -ForegroundColor Green
            $backendRunning = $true
            break
        } catch {
            $retries++
            if ($retries -lt $maxRetries) {
                Write-Host "   Still waiting... ($retries/$maxRetries)" -ForegroundColor Yellow
                Start-Sleep -Seconds 5
            } else {
                Write-Host "❌ Backend failed to start. Please check the backend window for errors." -ForegroundColor Red
                exit 1
            }
        }
    }
}

if ($backendRunning) {
    Write-Host ""
    Write-Host "🔥 Pre-warming cache (this prevents timeouts)..." -ForegroundColor Cyan
    Write-Host "   This may take 30-60 seconds on first load..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommendations" -UseBasicParsing -TimeoutSec 120
        Write-Host "✅ Cache pre-warmed! Dashboard will load instantly." -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Cache pre-warming timed out, but that's okay." -ForegroundColor Yellow
        Write-Host "   The dashboard will still work, just may take longer on first load." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "📊 Starting Streamlit Dashboard..." -ForegroundColor Cyan
    Write-Host "   Make sure streamlit_app.py has API_URL = 'http://127.0.0.1:8000' for local use" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if API_URL is set to local
    $streamlitContent = Get-Content "streamlit_app.py" -Raw
    if ($streamlitContent -match "API_URL = `"https://") {
        Write-Host "⚠️  WARNING: streamlit_app.py is pointing to Render URL." -ForegroundColor Yellow
        Write-Host "   For local development, change line 10 to:" -ForegroundColor Yellow
        Write-Host "   API_URL = 'http://127.0.0.1:8000'" -ForegroundColor Cyan
        Write-Host ""
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne "y") {
            Write-Host "Exiting. Please update streamlit_app.py first." -ForegroundColor Red
            exit 1
        }
    }
    
    # Start Streamlit
    streamlit run streamlit_app.py
    
} else {
    Write-Host ""
    Write-Host "❌ Could not start backend. Please check:" -ForegroundColor Red
    Write-Host "   1. Dependencies installed: pip install -r requirements.txt" -ForegroundColor Yellow
    Write-Host "   2. Port 8000 is not in use by another app" -ForegroundColor Yellow
    Write-Host "   3. Python environment is activated" -ForegroundColor Yellow
    Write-Host ""
}

