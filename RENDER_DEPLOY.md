# Deploy to Render - Step by Step

## 🚀 Quick Deployment (5 minutes)

### Option 1: Using Render Dashboard (Recommended)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up/Login with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this code

3. **Configure Service**
   - **Name**: `image-crop-api` (or any name you like)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (or `.` if needed)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (Optional but recommended)
   - Click "Advanced" → "Environment Variables"
   - Add:
     - `OUTPUT_DIR` = `./cropped_images`
     - `IMGBB_API_KEY` = Your ImgBB API key (get from https://api.imgbb.com/)
     - Or Cloudinary vars if using Cloudinary

5. **Deploy!**
   - Click "Create Web Service"
   - Wait 3-5 minutes for build and deployment
   - Your API will be at: `https://your-service-name.onrender.com`

### Option 2: Using render.yaml (Auto-config)

1. **Push to GitHub** (if not already)
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push
   ```

2. **Deploy via Render Dashboard**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render will auto-detect `render.yaml` and configure everything
   - Click "Apply"

## 🔑 Get ImgBB API Key (For Image Hosting)

1. Go to https://api.imgbb.com/
2. Sign up (free)
3. Get your API key
4. Add it to Render environment variables as `IMGBB_API_KEY`

## ✅ After Deployment

1. **Get your API URL**: `https://your-service-name.onrender.com`
2. **Test it**:
   ```bash
   curl -X POST "https://your-service-name.onrender.com/crop-image" \
     -H "Content-Type: application/json" \
     -d '{
       "image_url": "https://example.com/image.jpg",
       "use_detection": true,
       "detect_windows_only": true,
       "confidence_threshold": 0.3
     }'
   ```

3. **Update Vercel Environment Variable**:
   ```bash
   vercel env add PYTHON_API_URL production
   # Enter: https://your-service-name.onrender.com
   ```

## 📝 Important Notes

- **First deployment** takes 5-10 minutes (installing dependencies)
- **Free tier** has 15-minute sleep after inactivity
- **YOLO model** downloads automatically on first use (~6MB)
- **Cold starts** may take 30-60 seconds on free tier

## 🐛 Troubleshooting

**Build fails?**
- Check logs in Render dashboard
- Ensure `requirements.txt` has all dependencies
- Python version should be 3.9+

**Timeout errors?**
- Free tier has 10-second timeout
- Upgrade to paid plan for longer timeouts
- Or optimize image processing

**Images not uploading?**
- Add `IMGBB_API_KEY` environment variable
- Or configure Cloudinary/S3

## 🔗 Next Steps

Once deployed:
1. Copy your Render API URL
2. Set it in Vercel: `vercel env add PYTHON_API_URL production`
3. Test the full flow: Vercel → Render → Cloud Storage
