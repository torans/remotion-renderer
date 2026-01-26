# 🎬 Remotion Cloud Renderer

Cloud-based video renderer for Motion Graphics Agent using Remotion.

## 📋 Features

- ✅ Renders TSX code to MP4 videos
- ✅ REST API endpoint for agent integration
- ✅ Automatic cleanup of temporary files
- ✅ Progress tracking
- ✅ Cloud-ready (Render.com, Railway, etc.)

## 🚀 Quick Deploy to Render.com

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/remotion-renderer.git
git push -u origin main
```

### 2. Deploy on Render.com

1. Go to [render.com](https://render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` config
5. Click **Create Web Service**
6. Wait 3-5 minutes for deployment
7. Get your URL: `https://your-app.onrender.com`

### 3. Test the Deployment

```bash
curl https://your-app.onrender.com/
```

## 📡 API Endpoints

### POST `/render`

Render a video from TSX code.

**Request:**
```json
{
  "tsx_code": "import React from 'react'...",
  "composition_id": "MyVideo",
  "duration": 5,
  "width": 1080,
  "height": 1920,
  "fps": 30
}
```

**Response:**
```json
{
  "status": "success",
  "video_path": "/path/to/video.mp4",
  "filename": "MyVideo_1234567890.mp4",
  "composition_id": "MyVideo",
  "duration_seconds": 5,
  "render_time_seconds": 12.5,
  "file_size_mb": 2.3,
  "message": "Video rendered successfully in 12.5s"
}
```

### GET `/`

Health check endpoint.

### GET `/download/:filename`

Download a rendered video.

## 🔧 Local Development

```bash
# Install dependencies
npm install

# Start server
npm start

# Server runs on http://localhost:3000
```

## 🐍 Python Integration (Motion Graphics Agent)

Update your `Motion_tools.py`:

```python
import requests

RENDERER_URL = "https://your-app.onrender.com/render"

def _run(self, code_path: str, composition_id: str, output_name: str) -> str:
    # Read TSX code
    with open(code_path, 'r') as f:
        tsx_code = f.read()
    
    # Send to cloud renderer
    response = requests.post(
        RENDERER_URL,
        json={
            'tsx_code': tsx_code,
            'composition_id': composition_id,
            'duration': 5,
            'width': 1080,
            'height': 1920,
            'fps': 30
        },
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        return {
            "status": "success",
            "video_path": result['video_path'],
            "message": result['message']
        }
    else:
        return {
            "status": "failed",
            "error": response.text
        }
```

## 💰 Costs

### Render.com
- **FREE tier**: 750 hours/month (sleeps after 15min inactivity)
- **Starter ($7/mo)**: Always-on, faster
- **Standard ($25/mo)**: More resources

### Railway
- **FREE tier**: $5 credit/month
- **Pay-as-you-go**: ~$0.000463/min

## 🔒 Environment Variables

No API keys needed! Remotion is open source.

## 📝 Notes

- Rendering takes 10-30 seconds depending on video length
- FREE tier sleeps after 15min → first request takes 30-60s to wake up
- Upgrade to paid plan for production use
- Temporary files auto-cleanup after 5 seconds

## 🆘 Troubleshooting

**Error: "Module not found"**
- Make sure all dependencies are in `package.json`

**Error: "Timeout"**
- Increase timeout in your Python code to 180s
- Consider upgrading to paid tier for faster rendering

**Error: "Out of memory"**
- Upgrade to a larger Render.com plan
- Or use Railway with more memory

## 📧 Support

Created for Motion Graphics Agent integration.
For issues, check Remotion docs: https://remotion.dev
