# ✅ Vercel Deployment Complete!

## Your Vercel Endpoint

**Production URL**: `https://image-crop-90qrz97q0-aitons-projects-0358f994.vercel.app`

**API Endpoint**: `https://image-crop-90qrz97q0-aitons-projects-0358f994.vercel.app/api/crop-image`

## ⚠️ Important: Set Python API URL

Before using the endpoint, you need to:

1. **Deploy the Python API** (`app.py`) on Render/Railway/Fly.io
   - See `DEPLOY.md` for instructions
   - Your Python API will be at: `https://your-api.onrender.com`

2. **Set Environment Variable in Vercel**:
   ```bash
   vercel env add PYTHON_API_URL production
   # Enter: https://your-api.onrender.com
   ```

   Or via Vercel Dashboard:
   - Go to: https://vercel.com/aitons-projects-0358f994/image-crop-api/settings/environment-variables
   - Add: `PYTHON_API_URL` = `https://your-api.onrender.com`

## 🧪 Test the Endpoint

Once `PYTHON_API_URL` is set:

```bash
curl -X POST "https://image-crop-90qrz97q0-aitons-projects-0358f994.vercel.app/api/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "use_detection": true,
    "detect_windows_only": true,
    "confidence_threshold": 0.3,
    "clear_previous": true
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
      "bbox": {...}
    }
  ]
}
```

## 🔗 Quick Links

- **Vercel Dashboard**: https://vercel.com/aitons-projects-0358f994/image-crop-api
- **Deployment Logs**: `vercel inspect --logs`
- **Redeploy**: `vercel --prod`

## 📋 Next Steps

1. Deploy `app.py` on Render (see `DEPLOY.md`)
2. Set `PYTHON_API_URL` environment variable
3. Test the endpoint
4. Use in n8n workflows!
