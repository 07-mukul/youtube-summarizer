# YouTube Video Summarizer - Deployment Guide

## 📦 Project Overview
- **Frontend:** HTML/CSS/JavaScript (Deploy to Vercel)
- **Backend:** Flask API (Deploy to Render)
- **Features:** YouTube video summarization with AI

---

## 🚀 DEPLOYMENT STEPS (Full Tutorial)

### **PART 1: Deploy Backend to Render.com**

#### **Step 1.1: Create Render Account**
1. Go to https://render.com
2. Click **"Sign Up"** (top right)
3. Choose **"Sign up with GitHub"** or email
4. Complete signup

#### **Step 1.2: Push Code to GitHub**

**On your Windows PC:**

1. Open PowerShell in your project folder:
   ```powershell
   cd "C:\Users\youca\OneDrive\Desktop\project news"
   ```

2. Install Git (if not already installed):
   - Download from https://git-scm.com
   - Run installer with default settings

3. Initialize Git repository:
   ```powershell
   git init
   git add .
   git commit -m "Initial commit - YouTube Summarizer"
   ```

4. Go to https://github.com and create new repository:
   - Click **+** (top right) → **New repository**
   - Name: `youtube-summarizer`
   - Keep it **Public**
   - Click **Create repository**

5. Connect local repo to GitHub:
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/youtube-summarizer.git
   git branch -M main
   git push -u origin main
   ```

#### **Step 1.3: Create Render Service**

1. Log in to Render.com
2. Click **"New +"** (top right) → **"Web Service"**
3. Click **"Connect Repository"** → Select your `youtube-summarizer` repo
4. Fill in details:
   - **Name:** `youtube-summarizer-api`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Click **"Create Web Service"**
6. Wait 2-3 minutes for deployment (green dot = ready)
7. Copy the URL shown (e.g., `https://youtube-summarizer-api.onrender.com`)

#### **Step 1.4: Add Environment Variables to Render**

1. In Render dashboard, find your service
2. Go to **Settings** → scroll to **Environment Variables**
3. Add:
   ```
   GEMINI_API_KEY = [Your Google Gemini API Key]
   ```
4. Click **Save**
5. Service will restart automatically

---

### **PART 2: Deploy Frontend to Vercel**

#### **Step 2.1: Update Frontend URL**

Edit `index.html` to use your Render backend URL:

In VS Code, find this line (around line 264):
```javascript
const API_URL = 'http://localhost:5000';
```

Replace with:
```javascript
const API_URL = 'https://youtube-summarizer-api.onrender.com';
```

Then save and commit:
```powershell
git add index.html
git commit -m "Update API URL for deployment"
git push
```

#### **Step 2.2: Create Vercel Account**

1. Go to https://vercel.com
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub

#### **Step 2.3: Deploy on Vercel**

1. After login, click **"New Project"**
2. Select your `youtube-summarizer` repository
3. **Project Settings:**
   - Framework Preset: **Other** (since it's just HTML/CSS/JS)
   - Root Directory: `./` (leave default)
4. Click **"Deploy"**
5. Wait 1-2 minutes
6. Copy your Vercel URL (e.g., `https://youtube-summarizer.vercel.app`)

---

## ✅ Testing Your Deployment

### **Test Backend:**
```
https://youtube-summarizer-api.onrender.com/health
```
Should return: `{"status": "active", "message": "Service is running"}`

### **Test Frontend:**
```
https://youtube-summarizer.vercel.app
```
- Paste a YouTube URL
- Click "Summarize Video"
- Should generate summary!

---

## 📝 Key Points

| Component | Where | URL |
|-----------|-------|-----|
| Backend API | Render | `https://youtube-summarizer-api.onrender.com` |
| Frontend | Vercel | `https://youtube-summarizer.vercel.app` |
| GitHub Repo | GitHub | `https://github.com/YOUR_USERNAME/youtube-summarizer` |

## 🔧 Future Updates

To update your deployed app:

```powershell
# Make changes locally
# Then:
git add .
git commit -m "Your update message"
git push
```

- **Render** will auto-redeploy backend
- **Vercel** will auto-redeploy frontend

---

## ⚠️ Important Notes

1. **Environment Variables:**
   - Never push `.env` file to GitHub (it's in `.gitignore`)
   - Always set API keys in deployment platform settings

2. **Cold Starts:**
   - Render free tier may take 30-60 seconds on first request (normal)
   - Upgrade to paid for instant response

3. **API Limits:**
   - Free tier of Render: 750 hours/month
   - Free tier of Vercel: Unlimited
   - Gemini API: Free quota applies

---

## 🆘 Troubleshooting

**Q: Frontend shows blank screen?**
- A: Check browser console (F12) for CORS errors
- Make sure API_URL in index.html is correct

**Q: Backend gives 500 error?**
- A: Check Render logs → Logs tab in dashboard
- Verify GEMINI_API_KEY is set in Render environment variables

**Q: Takes 60+ seconds to respond?**
- A: Cold start (normal on Render free tier)
- First request wakes up the server

---

## 📚 Resources

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Flask Guide: https://flask.palletsprojects.com

