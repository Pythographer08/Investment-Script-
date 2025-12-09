# Setting Up Daily Email Automation on Windows

## Step 1: Open Task Scheduler
- Press **Win + R**, type `taskschd.msc`, hit Enter

## Step 2: Create Basic Task
1. Click **"Create Basic Task..."** (right sidebar)
2. **Name**: `Daily Investment Report`
3. **Description**: `Sends daily investment recommendations CSV via email`
4. Click **Next**

## Step 3: Set Trigger
1. Choose **Daily**
2. Click **Next**
3. Set **Start date**: Today
4. Set **Time**: 8:00 AM (or your preferred time)
5. Set **Recur every**: 1 days
6. Click **Next**

## Step 4: Find Your Python Path (Do This First!)

Run this in PowerShell to find your exact Python executable path:
```powershell
python -c "import sys; print(sys.executable)"
```

Or try:
```powershell
where.exe python
```

Common locations:
- `C:\Users\niki3\AppData\Local\Programs\Python\Python310\python.exe`
- `C:\Users\niki3\AppData\Local\Programs\Python\Python311\python.exe`
- `C:\Python310\python.exe`
- Or wherever you installed Python

**Copy the full path** (it will look like one of the above)

## Step 5: Set Action
1. Choose **Start a program**
2. Click **Next**
3. **Program/script**: 
   ```
   [PASTE YOUR PYTHON PATH HERE]
   ```
   Example: `C:\Users\niki3\AppData\Local\Programs\Python\Python310\python.exe`
4. **Add arguments**:
   ```
   C:\Users\niki3\.streamlit\deploy_daily_report.py
   ```
5. **Start in**:
   ```
   C:\Users\niki3\.streamlit
   ```
6. Click **Next**, then **Finish**

## Step 6: Test It
1. Right-click your new task → **Run**
2. Check your email inbox
3. If it fails, right-click task → **Properties** → **History** tab to see errors

## Step 7: Make It Run Even If Computer Was Off/Sleeping

**Important**: If your computer is completely OFF, it cannot run tasks. However, you can make it run when the computer wakes up:

1. Right-click your task → **Properties**
2. Go to **Settings** tab
3. Check these boxes:
   - ✅ **"Run task as soon as possible after a scheduled start is missed"**
   - ✅ **"If the task fails, restart every:"** (set to 10 minutes, max 3 restarts)
4. Go to **Conditions** tab
5. Check:
   - ✅ **"Wake the computer to run this task"** (if you want it to wake from sleep)
   - Uncheck **"Start the task only if the computer is on AC power"** (if you want it to run on battery)
6. Click **OK**

**Limitation**: This only works if your computer is **sleeping/hibernating**, not completely powered off.

---

## ⚠️ Better Solution: Deploy to Cloud (Runs 24/7 Even When PC is Off)

If you want the email to send **even when your computer is completely off**, deploy to a cloud service. See `cloud_deployment.md` for Railway/Heroku setup.

---

## Step 8: Other Advanced Settings (Optional)
- **Properties** → **General**: Check "Run whether user is logged on or not" (requires password)
- **Properties** → **History**: Enable "Enable All Tasks History" to debug issues

