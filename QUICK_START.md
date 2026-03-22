# 🚀 QUICK DEPLOYMENT CHECKLIST

## Before You Start
- [ ] GitHub Account (https://github.com)
- [ ] Render Account (https://render.com)
- [ ] Vercel Account (https://vercel.com)
- [ ] Google Gemini API Key (from .env file)

---

## ⚡ 5-MINUTE QUICK START

### Phase 1: Git & GitHub (3 minutes)
```powershell
# 1. Open PowerShell in project folder
cd "C:\Users\youca\OneDrive\Desktop\project news"

# 2. Initialize git
git init
git add .
git commit -m "Initial commit"

# 3. Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/youtube-summarizer.git
git branch -M main
git push -u origin main
```

### Phase 2: Deploy Backend to Render (2 minutes)
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Select your GitHub repo
4. Settings:
   - Start Command: `gunicorn app:app`
5. Click "Create Web Service"
6. Wait for deployment ✅
7. Go to Settings → Environment Variables
8. Add: `GEMINI_API_KEY = YOUR_KEY`
9. Copy the deployed URL (e.g., `https://youtube-summarizer-api.onrender.com`)

### Phase 3: Update & Deploy Frontend (1 minute)
1. Edit `index.html` - Change line ~264:
   ```javascript
   const API_URL = 'https://youtube-summarizer-api.onrender.com';
   ```
2. Save and push:
   ```powershell
   git add index.html
   git commit -m "Update API URL"
   git push
   ```
3. Go to https://vercel.com/dashboard
4. Click "New Project" → Select your repo
5. Click "Deploy" 🎉

---

## ✅ You're Done!

- Backend: `https://youtube-summarizer-api.onrender.com`
- Frontend: Your Vercel URL (shown in dashboard)

Visit your Vercel URL and test!

---

## 📱 What to Test

1. **Health Check:** `{YOUR_RENDER_URL}/health`
2. **Paste YouTube URL:** In the web app
3. **Click Summarize:** Should show loading animation
4. **Result:** 10-point summary appears

---

## 🔄 Updates Later

```powershell
# Make code changes
# Then:
git add .
git commit -m "Your change"
git push
```

Both services auto-redeploy! ✅

