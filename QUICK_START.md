# Quick Start: Deploy to Vercel

## 🚀 Quick Deployment Steps

### 1. Deploy Python API (5 minutes)

**Option A: Render.com (Easiest)**
1. Go to https://render.com
2. Sign up → New Web Service
3. Connect GitHub repo
4. Settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add env vars (optional):
   - `IMGBB_API_KEY` (get from https://api.imgbb.com/)
   - Or `CLOUDINARY_*` vars
6. Deploy!

**Your API URL**: `https://your-app.onrender.com`

### 2. Deploy Vercel Endpoint (2 minutes)

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Set your Python API URL
vercel env add PYTHON_API_URL production
# Enter: https://your-app.onrender.com

# Deploy!
vercel --prod
```

**Your Vercel URL**: `https://your-project.vercel.app/api/crop-image`

### 3. Test It! 🎉

```bash
curl -X POST "https://your-project.vercel.app/api/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "use_detection": true,
    "detect_windows_only": true,
    "confidence_threshold": 0.3
  }'
```

## 📝 Response Format

```json
{
  "status": "success",
  "job_id": "abc123...",
  "saved_count": 3,
  "saved_files": [
    {
      "url": "https://i.ibb.co/.../001_window_1.jpg",
      "filename": "001_window_1.jpg",
      "label": "window_1",
      "bbox": {
        "x": 100,
        "y": 200,
        "width": 300,
        "height": 400
      }
    }
  ]
}
```

## 🔑 Get Image Hosting API Key (Optional)

**ImgBB (Free & Easy)**:
1. Go to https://api.imgbb.com/
2. Sign up → Get API key
3. Add to Render env vars: `IMGBB_API_KEY=your_key`

**Cloudinary (Better for Production)**:
1. Go to https://cloudinary.com
2. Sign up → Get credentials
3. Add to Render:
   - `CLOUDINARY_CLOUD_NAME=xxx`
   - `CLOUDINARY_API_KEY=xxx`
   - `CLOUDINARY_API_SECRET=xxx`

## ⚠️ Important Notes

- **Vercel timeout**: 10s (free) / 60s (pro)
- **Python API** handles heavy processing (YOLO, OpenCV)
- **Images** are uploaded to cloud storage and URLs returned
- **Previous batches** auto-deleted when `clear_previous: true`

## 🐛 Troubleshooting

**"PYTHON_API_URL not set"**:
- Set it in Vercel dashboard → Settings → Environment Variables

**"Images not uploading"**:
- Add `IMGBB_API_KEY` or Cloudinary credentials to Render

**"Timeout errors"**:
- Upgrade Vercel to Pro (60s timeout)
- Or optimize Python API response time
