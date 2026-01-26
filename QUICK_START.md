# ⚡ QUICK START - 5 MINUTE DEPLOYMENT

## 📥 **STEP 1: DOWNLOAD & EXTRACT**

1. Download `remotion-renderer.zip`
2. Extract to a folder

---

## 🚀 **STEP 2: DEPLOY (CHOOSE ONE)**

### **OPTION A: Render.com (Recommended)**

```bash
cd remotion-renderer

# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/remotion-renderer.git
git push -u origin main

# 2. Go to render.com
# 3. New + → Web Service → Connect GitHub repo
# 4. Click "Create Web Service"
# 5. Wait 5 minutes ⏱️
# 6. Copy URL: https://your-app.onrender.com
```

### **OPTION B: Railway (Alternative)**

```bash
# Same as above, but deploy to railway.app instead
```

---

## 🔧 **STEP 3: UPDATE PYTHON CODE**

Open your `Motion_tools.py` and change:

```python
# OLD:
RENDERER_URL = "http://localhost:3000/render"

# NEW (replace with your URL):
RENDERER_URL = "https://your-app.onrender.com/render"
```

**OR** set environment variable:

```bash
export RENDERER_URL="https://your-app.onrender.com/render"
```

---

## ✅ **STEP 4: TEST**

```bash
curl https://your-app.onrender.com/

# Should return:
# {"status":"ok","message":"Remotion Cloud Renderer is running"}
```

---

## 🎬 **STEP 5: RUN YOUR AGENT**

```bash
cd splicr-agents
python test_motion_graphics.py
```

**DONE! 🎉**

---

## 📝 **WHAT YOU GET:**

✅ Cloud renderer running 24/7  
✅ No local dependencies needed  
✅ Automatic video rendering  
✅ FREE tier available  
✅ Easy scaling when needed  

---

## 💰 **COSTS:**

- **FREE**: 750 hours/month (sleeps after 15min)
- **PAID**: $7/month (always-on, faster)

Start FREE, upgrade when needed!

---

## 🆘 **NEED HELP?**

Check `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.

---

## 📂 **FILES INCLUDED:**

- `package.json` - Dependencies
- `server.js` - API server
- `renderer.js` - Remotion logic
- `render.yaml` - Render.com config
- `Motion_tools_CLOUD.py` - Updated tools
- `README.md` - Full documentation
- `DEPLOYMENT_GUIDE.md` - Step-by-step guide
