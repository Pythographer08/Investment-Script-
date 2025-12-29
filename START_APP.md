# How to Start the App from Scratch

## Quick Start (Recommended)

### Step 1: Start the Backend API

Open **Terminal 1** (PowerShell or Command Prompt):

```bash
cd C:\Users\niki3\.streamlit
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Wait for this message:** `Uvicorn running on http://127.0.0.1:8000`

✅ **Backend is ready when you see:** `Application startup complete.`

### Step 2: Pre-warm the Cache (Optional but Recommended)

**Why?** The first request fetches news for 109 stocks, which takes 30-60 seconds. Pre-warming loads the cache so your dashboard loads instantly.

Open **Terminal 2** (while Terminal 1 is still running):

```bash
# Pre-warm the cache by making a request
curl http://127.0.0.1:8000/recommendations
```

Or use PowerShell:
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/recommendations" -UseBasicParsing
```

**Wait 30-60 seconds** for the first request to complete. You'll see progress logs in Terminal 1.

### Step 3: Start the Streamlit Dashboard

**Keep Terminal 1 running!** Open **Terminal 3**:

```bash
cd C:\Users\niki3\.streamlit
streamlit run streamlit_app.py
```

**Wait for this message:** `You can now view your Streamlit app in your browser.`

✅ **Dashboard URL:** http://localhost:8501

---

## What You'll See

### First Load (No Cache)
- ⏱️ **Loading time:** 30-60 seconds
- 📊 Dashboard will show "Loading recommendations..." spinner
- ✅ Once loaded, all features work normally

### Subsequent Loads (With Cache)
- ⚡ **Loading time:** < 1 second
- 📊 Dashboard loads instantly
- ✅ Cache lasts 5 minutes, then refreshes automatically

---

## Troubleshooting

### ❌ "Connection refused" or "Failed to connect"
**Solution:** Make sure Terminal 1 (backend) is running and shows `Application startup complete.`

### ❌ Dashboard shows timeout error
**Solution:** 
1. Pre-warm the cache first (Step 2 above)
2. Or wait 30-60 seconds on first load - this is normal!

### ❌ Backend crashes or shows errors
**Solution:**
1. Check that all dependencies are installed: `pip install -r requirements.txt`
2. Make sure port 8000 is not in use by another app
3. Check Terminal 1 for error messages

### ❌ Streamlit shows "Unable to connect to backend"
**Solution:**
1. Verify backend is running: Open http://127.0.0.1:8000/docs in browser
2. Check `streamlit_app.py` has `API_URL = "http://127.0.0.1:8000"` (for local) or your Render URL (for production)

---

## Production (Render + Streamlit Cloud)

### Backend (Render)
- Already deployed at: `https://investment-script.onrender.com`
- Cache is shared across all users
- First user each 5 minutes triggers cache refresh

### Frontend (Streamlit Cloud)
- Already deployed and connected to Render backend
- Uses production API URL automatically
- No local setup needed!

---

## Pro Tips

1. **Always pre-warm cache** before demoing the app
2. **Keep backend running** - don't close Terminal 1
3. **Check cache status** - Visit http://127.0.0.1:8000/health to verify backend is alive
4. **Monitor logs** - Terminal 1 shows progress for news fetching

---

## Expected Performance

| Scenario | Time | Notes |
|----------|------|-------|
| First load (cold cache) | 30-60s | Normal - fetching 109 stocks |
| Subsequent loads (warm cache) | < 1s | Fast - using cached data |
| Cache refresh | Every 5 min | Automatic |
| Individual stock analysis | 2-5s | On-demand endpoints |

---

## Summary

**For fastest experience:**
1. Start backend (Terminal 1)
2. Pre-warm cache (Terminal 2) - wait 30-60s
3. Start Streamlit (Terminal 3)
4. Enjoy instant dashboard! 🚀

