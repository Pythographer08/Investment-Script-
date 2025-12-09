# Cloud Deployment Guide - Run Daily Emails Even When PC is Off

Deploy your daily email script to a cloud service so it runs automatically 24/7, even when your computer is off.

## Option 1: Railway (Recommended - Easiest)

Railway offers free tier with scheduled jobs.

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub
3. Create a new project

### Step 2: Prepare Your Code
Create these files in your project:

**`railway.json`** (scheduler config):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python deploy_daily_report.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**`Procfile`** (for Heroku compatibility):
```
worker: python deploy_daily_report.py
```

### Step 3: Deploy to Railway
1. In Railway dashboard, click **"New Project"**
2. Select **"Deploy from GitHub repo"** (or upload your code)
3. Add these **Environment Variables**:
   - `GMAIL_USER` = your Gmail
   - `GMAIL_APP_PASSWORD` = your app password
   - `RECIPIENT_EMAIL` = recipient email

### Step 4: Set Up Cron Job
Railway doesn't have built-in cron, so use **cron-job.org** (free):

1. Go to https://cron-job.org
2. Create account
3. Create new cron job:
   - **URL**: `https://your-railway-app.railway.app/run` (if you add an endpoint)
   - **Schedule**: Daily at 8:00 AM
   - **Request Method**: GET

**OR** use Railway's scheduled deployments with a webhook trigger.

---

## Option 2: Heroku (Free Tier Discontinued, Paid Only)

Heroku Scheduler add-on costs ~$25/month. Railway is cheaper/free.

### Step 1: Create Heroku App
```bash
heroku create your-app-name
heroku addons:create scheduler:standard
```

### Step 2: Set Environment Variables
```bash
heroku config:set GMAIL_USER=yourgmail@gmail.com
heroku config:set GMAIL_APP_PASSWORD=your_app_password
heroku config:set RECIPIENT_EMAIL=recipient@example.com
```

### Step 3: Deploy
```bash
git push heroku main
```

### Step 4: Schedule Job
1. Go to Heroku dashboard → your app → **Scheduler**
2. Add job: `python deploy_daily_report.py`
3. Set schedule: Daily at 8:00 AM

---

## Option 3: PythonAnywhere (Free Tier Available)

Good for simple scheduled tasks.

### Step 1: Sign Up
1. Go to https://www.pythonanywhere.com
2. Create free account

### Step 2: Upload Your Code
1. Go to **Files** tab
2. Upload your `.streamlit` folder contents
3. Upload `requirements.txt`

### Step 3: Install Dependencies
1. Go to **Consoles** → **Bash**
2. Run:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

### Step 4: Set Environment Variables
1. Create `.env` file in your home directory
2. Add your Gmail credentials

### Step 5: Schedule Task
1. Go to **Tasks** tab
2. Click **"Create a new scheduled task"**
3. Set:
   - **Command**: `python3.10 /home/yourusername/deploy_daily_report.py`
   - **Schedule**: Daily at 8:00 AM
4. Save

**Free tier limitation**: Tasks only run when you've logged in within the last 3 months.

---

## Option 4: GitHub Actions (Free, Best for Code Repos)

If your code is in a GitHub repo, use GitHub Actions (free for public repos).

### Step 1: Create Workflow File
Create `.github/workflows/daily-email.yml`:

```yaml
name: Daily Investment Report

on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily
  workflow_dispatch:  # Allow manual trigger

jobs:
  send-email:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run daily report
        env:
          GMAIL_USER: ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
          RECIPIENT_EMAIL: ${{ secrets.RECIPIENT_EMAIL }}
        run: |
          python deploy_daily_report.py
```

### Step 2: Add Secrets
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add:
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
   - `RECIPIENT_EMAIL`

### Step 3: Commit and Push
```bash
git add .github/workflows/daily-email.yml
git commit -m "Add daily email workflow"
git push
```

The workflow will run automatically every day at 8 AM UTC.

---

## Recommendation

**For simplicity**: Use **GitHub Actions** if your code is already in a repo (free, reliable, no server management).

**For standalone**: Use **PythonAnywhere** free tier (simple, no credit card needed).

**For production**: Use **Railway** (modern, good free tier, easy deployment).

