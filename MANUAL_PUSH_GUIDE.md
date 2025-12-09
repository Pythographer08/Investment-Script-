# Manual Push to GitHub - Step by Step

Since automated push might need authentication, here's how to do it manually:

## Option 1: Use the PowerShell Script (Easiest)

1. Open PowerShell in your project folder:
   ```powershell
   cd C:\Users\niki3\.streamlit
   ```

2. Run the script:
   ```powershell
   .\push_to_github.ps1
   ```

3. If it asks for credentials:
   - **Username**: Your GitHub username (`Pythographer08`)
   - **Password**: Use a **Personal Access Token** (NOT your GitHub password)
     - Go to: https://github.com/settings/tokens
     - Click "Generate new token (classic)"
     - Name it: "Investment Script Push"
     - Check `repo` scope
     - Copy the token and use it as password

## Option 2: Manual Commands (If Script Doesn't Work)

Run these commands one by one in PowerShell:

```powershell
cd C:\Users\niki3\.streamlit

# Initialize git (if not done)
git init

# Add all files
git add -A

# Commit
git commit -m "Initial commit: investment recommendation app"

# Set remote
git remote add origin https://github.com/Pythographer08/Investment-Script-.git

# Set branch
git branch -M main

# Push (will ask for credentials)
git push -u origin main
```

## If Push Fails with Authentication Error

GitHub no longer accepts passwords. You need a **Personal Access Token**:

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Name: `Investment Script Push`
4. Expiration: `90 days` (or your preference)
5. Check these scopes:
   - ✅ `repo` (full control of private repositories)
6. Click **"Generate token"**
7. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
8. When git asks for password, paste the token instead

## Verify It Worked

After pushing, check:
- https://github.com/Pythographer08/Investment-Script-

You should see all your files:
- `streamlit_app.py`
- `backend/main.py`
- `deploy_daily_report.py`
- `.github/workflows/daily-email.yml`
- `requirements.txt`
- etc.

## Troubleshooting

**Error: "remote origin already exists"**
```powershell
git remote remove origin
git remote add origin https://github.com/Pythographer08/Investment-Script-.git
```

**Error: "nothing to commit"**
```powershell
git add -A
git status  # Check what files are staged
```

**Error: "authentication failed"**
- Make sure you're using a Personal Access Token, not your GitHub password
- Token must have `repo` scope checked

