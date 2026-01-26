# 🚀 DEPLOYMENT GUIDE - STEP BY STEP

## 📦 **FILES CREATED:**

```
remotion-renderer/
├── package.json           # Node.js dependencies
├── server.js              # Express API server  
├── renderer.js            # Remotion rendering logic
├── render.yaml            # Render.com config
├── .gitignore            # Git ignore rules
├── README.md             # Documentation
└── Motion_tools_CLOUD.py # Updated Python tools
```

---

## ☁️ **OPTION 1: RENDER.COM (RECOMMENDED - EASIEST)**

### **Step 1: Push to GitHub**

```bash
cd remotion-renderer

git init
git add .
git commit -m "Initial commit - Remotion cloud renderer"
git branch -M main

# Create GitHub repo at https://github.com/new
# Then:
git remote add origin https://github.com/YOUR_USERNAME/remotion-renderer.git
git push -u origin main
```

### **Step 2: Deploy to Render.com**

1. Go to **[render.com](https://render.com)** and sign up (free)
2. Click **New +** → **Web Service**
3. Click **Connect a repository** → Connect GitHub
4. Select your `remotion-renderer` repository
5. Render auto-detects `render.yaml` ✅
6. Click **Create Web Service**
7. Wait **3-5 minutes** for deployment
8. Copy your URL: `https://remotion-renderer-xxxx.onrender.com`

### **Step 3: Test Deployment**

```bash
# Test health check
curl https://your-app.onrender.com/

# Should return:
# {"status":"ok","message":"Remotion Cloud Renderer is running","version":"1.0.0"}
```

### **Step 4: Update Python Code**

Replace in your `Motion_tools.py`:

```python
# OLD (local):
RENDERER_URL = "http://localhost:3000/render"

# NEW (cloud):
RENDERER_URL = "https://your-app.onrender.com/render"
```

Or set environment variable:
```bash
export RENDERER_URL="https://your-app.onrender.com/render"
```

---

## ☁️ **OPTION 2: RAILWAY (ALTERNATIVE)**

### **Step 1: Push to GitHub** (same as above)

### **Step 2: Deploy to Railway**

1. Go to **[railway.app](https://railway.app)** and sign up
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `remotion-renderer`
4. Railway auto-detects Node.js ✅
5. Wait 2-3 minutes
6. Click **Settings** → Copy your domain
7. Your URL: `https://remotion-renderer-production.up.railway.app`

### **Step 3: Test & Update** (same as Render.com)

---

## 💰 **PRICING COMPARISON:**

| Platform | Free Tier | Paid |
|----------|-----------|------|
| **Render.com** | 750hrs/month (sleeps) | $7/mo (always-on) |
| **Railway** | $5 credit/month | Pay-as-you-go (~$5-10/mo) |

**Recommendation:** Start with Render.com free tier!

---

## 🧪 **TESTING YOUR DEPLOYMENT:**

### **Full Render Test:**

```python
import requests

# Your cloud URL
url = "https://your-app.onrender.com/render"

# Test code
tsx_code = """
import React from 'react';
import { useCurrentFrame, AbsoluteFill } from 'remotion';

export const compositionConfig = {
  id: 'TestVideo',
  durationInSeconds: 3,
  fps: 30,
  width: 1080,
  height: 1920,
};

const TestVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = Math.min(1, frame / 30);
  
  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a2e', justifyContent: 'center', alignItems: 'center' }}>
      <h1 style={{ color: 'white', fontSize: 80, opacity }}>
        Hello World!
      </h1>
    </AbsoluteFill>
  );
};

export default TestVideo;
"""

# Send request
response = requests.post(url, json={
    'tsx_code': tsx_code,
    'composition_id': 'TestVideo',
    'duration': 3,
    'width': 1080,
    'height': 1920,
    'fps': 30
}, timeout=180)

print(response.json())
```

**Expected output:**
```json
{
  "status": "success",
  "video_path": "/app/output/TestVideo_1234567890.mp4",
  "filename": "TestVideo_1234567890.mp4",
  "composition_id": "TestVideo",
  "duration_seconds": 3,
  "render_time_seconds": 12.5,
  "file_size_mb": 0.8,
  "message": "Video rendered successfully in 12.5s"
}
```

---

## 🔧 **INTEGRATION WITH YOUR AGENT:**

Copy the **updated** `Motion_tools_CLOUD.py` to replace your current `Motion_tools.py`:

```bash
cp Motion_tools_CLOUD.py ../splicr-agents/tools/Motion_tools.py
```

Then update the URL:
```python
# At the top of Motion_tools.py
RENDERER_URL = "https://your-app.onrender.com/render"
```

---

## ⚠️ **IMPORTANT NOTES:**

1. **First request on FREE tier takes 30-60 seconds** (cold start)
2. **Subsequent requests are fast** (10-30 seconds)
3. **Upgrade to $7/mo for always-on** (no cold starts)
4. **Rendering time:** 10-30 seconds per video
5. **Timeout:** Set to 180 seconds (3 minutes) in your Python code

---

## 🆘 **TROUBLESHOOTING:**

### **Error: "Cannot find module '@remotion/bundler'"**
- Render.com is still installing dependencies
- Wait another 2-3 minutes
- Check build logs in Render.com dashboard

### **Error: "Timeout after 120 seconds"**
- Increase timeout in Python:
```python
response = requests.post(url, json=data, timeout=180)  # 3 minutes
```

### **Error: "Service Unavailable"**
- Free tier is sleeping (15min inactivity)
- First request wakes it up (takes 30-60s)
- Consider upgrading to paid plan

---

## ✅ **QUICK CHECKLIST:**

- [ ] Files created in `remotion-renderer/` folder
- [ ] Pushed to GitHub
- [ ] Deployed to Render.com or Railway
- [ ] Got your cloud URL
- [ ] Updated `RENDERER_URL` in Python
- [ ] Tested with curl or Python script
- [ ] Integrated with Motion Graphics Agent

---

## 🎉 **YOU'RE DONE!**

Your Motion Graphics Agent can now render videos in the cloud! 🚀

**Next steps:**
1. Test with your full agent workflow
2. Monitor render times and costs
3. Upgrade to paid plan when ready for production
