# Deployment Guide

## Architecture

This solution uses a **two-tier architecture**:

1. **Python API** (deployed on Render/Railway/Fly.io) - Handles heavy processing (YOLO, OpenCV)
2. **Vercel Endpoint** - Lightweight proxy that calls the Python API

## Step 1: Deploy Python API

### Option A: Render.com (Recommended)

1. Go to [Render.com](https://render.com) and create an account
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `image-crop-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `OUTPUT_DIR`: `./cropped_images` (optional)
   - `IMGBB_API_KEY`: Your ImgBB API key (optional, for image hosting)
6. Deploy!

Your API will be available at: `https://your-api.onrender.com`

### Option B: Railway

1. Go to [Railway.app](https://railway.app)
2. Create new project from GitHub
3. Add `requirements.txt` and `app.py`
4. Railway auto-detects Python and deploys
5. Set environment variables as above

### Option C: Fly.io

```bash
fly launch
fly deploy
```

## Step 2: Update Python API to Return URLs

The Python API (`app.py`) has been updated to:
- Upload cropped images to cloud storage (ImgBB/Cloudinary/S3)
- Return URLs in the response instead of local paths

**Important**: Configure image hosting:

### Option 1: ImgBB (Free, Easy)

1. Get API key from [imgbb.com](https://api.imgbb.com/)
2. Set environment variable: `IMGBB_API_KEY=your_key`

### Option 2: Cloudinary (Recommended for Production)

Update `upload_to_cloud_storage()` in `app.py`:

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def upload_to_cloud_storage(img_bytes, filename):
    img_bytes.seek(0)
    result = cloudinary.uploader.upload(
        img_bytes,
        folder="cropped-images",
        public_id=filename
    )
    return result["secure_url"]
```

### Option 3: AWS S3

Similar approach using boto3.

## Step 3: Deploy Vercel Endpoint

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Set Environment Variable**:
   ```bash
   vercel env add PYTHON_API_URL
   # Enter: https://your-api.onrender.com
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

Or deploy via GitHub:
1. Push code to GitHub
2. Import project in [Vercel Dashboard](https://vercel.com)
3. Add environment variable: `PYTHON_API_URL=https://your-api.onrender.com`
4. Deploy!

## Step 4: Test the Endpoint

Your Vercel endpoint will be: `https://your-project.vercel.app/api/crop-image`

**Test with curl**:
```bash
curl -X POST "https://your-project.vercel.app/api/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "use_detection": true,
    "detect_windows_only": true,
    "confidence_threshold": 0.3,
    "clear_previous": true
  }'
```

**Response**:
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
    },
    ...
  ]
}
```

## Environment Variables

### Python API (Render/Railway):
- `OUTPUT_DIR`: Local storage path (optional)
- `IMGBB_API_KEY`: For image hosting (optional)
- Or `CLOUDINARY_*` variables if using Cloudinary

### Vercel:
- `PYTHON_API_URL`: URL of your deployed Python API

## Notes

- Vercel has a 10-second timeout on free tier (60s on Pro)
- The Python API handles the heavy processing
- Cropped images are uploaded to cloud storage and URLs are returned
- Previous batches are automatically deleted when `clear_previous: true`
