# 🚀 PUSH YOUR PROJECT TO GITHUB - STEP BY STEP

## Your GitHub Username: **07-mukul**

---

## ✅ STEPS TO UPLOAD BOTH FRONTEND & BACKEND

### **Step 1: Configure Git (One Time)**

Open PowerShell and run:

```powershell
cd "C:\Users\youca\OneDrive\Desktop\project news"

git config user.name "07-mukul"
git config user.email "your-email@gmail.com"
```

(Replace `your-email@gmail.com` with your actual email)

---

### **Step 2: Add All Files & Create First Commit**

```powershell
git add .
git status
```

You should see ALL your files (green):
- ✅ app.py
- ✅ index.html
- ✅ package.json
- ✅ requirements.txt
- ✅ .gitignore
- ✅ Procfile
- ✅ DEPLOYMENT_GUIDE.md
- ✅ QUICK_START.md
- ✅ .env (hidden by .gitignore)
- ✅ node_modules/ (hidden by .gitignore)
- ✅ venv/ (hidden by .gitignore)

Then commit:

```powershell
git commit -m "Initial commit: YouTube Video Summarizer with Flask backend and HTML frontend"
```

---

### **Step 3: Create Repository on GitHub**

1. Go to https://github.com/07-mukul
2. Click **+** (top right) → **New repository**
3. Fill in:
   - **Repository name:** `youtube-summarizer`
   - **Description:** `AI-powered YouTube video summarizer using Flask and Gemini API`
   - **Visibility:** Public ✅
4. Click **Create repository**

You'll see instructions. Don't follow them - instead use Step 4 below.

---

### **Step 4: Push to GitHub**

```powershell
git remote add origin https://github.com/07-mukul/youtube-summarizer.git
git branch -M main
git push -u origin main
```

**First time it will ask for authentication:**
- Use your GitHub password OR Personal Access Token

---

## ✨ Done!

Your repository is now at:
```
https://github.com/07-mukul/youtube-summarizer
```

---

## 📁 What Gets Uploaded?

| File | Backend | Frontend | Upload |
|------|---------|----------|--------|
| app.py | ✅ | - | ✅ |
| index.html | - | ✅ | ✅ |
| package.json | - | ✅ | ✅ |
| requirements.txt | ✅ | - | ✅ |
| .env | ✅ | - | ❌ (Hidden - Safe!) |
| venv/ | ✅ | - | ❌ (Hidden) |
| node_modules/ | - | ✅ | ❌ (Hidden) |
| __pycache__/ | ✅ | - | ❌ (Hidden) |

---

## 🔄 Future Updates

Once pushed, updating is easy:

```powershell
# Make changes in VS Code
# Then:
git add .
git commit -m "Your change description"
git push
```

Done! Changes appear on GitHub instantly! ✅

---

## ⚡ Quick Command Summary

```powershell
# One time setup
git config user.name "07-mukul"
git config user.email "your-email@gmail.com"

# Initial push
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/07-mukul/youtube-summarizer.git
git branch -M main
git push -u origin main

# Future updates
git add .
git commit -m "Your message"
git push
```

---

Now run these commands in PowerShell! 🚀
