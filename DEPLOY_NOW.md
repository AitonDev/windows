# 🚀 Deploy to Render - Do This Now!

## Step 1: Create GitHub Repository (2 minutes)

1. **Go to**: https://github.com/new
2. **Repository name**: `image-crop-api`
3. **Description**: `Image crop API with window detection`
4. **Visibility**: Public (or Private)
5. **⚠️ IMPORTANT**: Do NOT check "Add a README file"
6. **Click**: "Create repository"

## Step 2: Push Code to GitHub

After creating the repo, GitHub will show you commands. **Run these in your terminal**:

```bash
cd /Users/vikrantsinghjamwal/Desktop/Windows

# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/image-crop-api.git
git branch -M main
git push -u origin main
```

**Note**: You'll be prompted for GitHub username and password/token.

## Step 3: Deploy on Render (3 minutes)

1. **Go to**: https://dashboard.render.com
2. **Sign up/Login** with GitHub
3. **Click**: "New +" → "Web Service"
4. **Connect** your GitHub account (if not already)
5. **Select repository**: `image-crop-api`
6. **Configure**:
   - **Name**: `image-crop-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: `pip install -r requirements-light.txt` *(use `requirements.txt` only if you need auto window/object detection)*
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
7. **Click**: "Create Web Service"

## Step 4: Wait for Deployment (5-10 minutes)

- First build takes 5-10 minutes
- Watch the logs in Render dashboard
- Your API will be at: `https://image-crop-api.onrender.com` (or similar)

## Step 5: Update Vercel Environment Variable

Once Render is deployed:

```bash
vercel env add PYTHON_API_URL production
# Enter: https://image-crop-api.onrender.com
```

Or via Vercel Dashboard:
- Go to: https://vercel.com/aitons-projects-0358f994/image-crop-api/settings/environment-variables
- Add: `PYTHON_API_URL` = `https://image-crop-api.onrender.com`

## ✅ Test It!

**Light build (free tier)** – send bounding boxes manually:

```bash
curl -X POST "https://image-crop-api.onrender.com/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "bounding_boxes": [
      {"x": 100, "y": 100, "width": 200, "height": 200, "label": "window1"}
    ]
  }'
```

**Full build** (if you use `requirements.txt` and have detection):

```bash
curl -X POST "https://image-crop-api.onrender.com/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "use_detection": true,
    "detect_windows_only": true,
    "confidence_threshold": 0.3
  }'
```

## 🎉 Done!

Your full stack is now deployed:
- **Vercel**: https://image-crop-90qrz97q0-aitons-projects-0358f994.vercel.app/api/crop-image
- **Render**: https://image-crop-api.onrender.com/crop-image
