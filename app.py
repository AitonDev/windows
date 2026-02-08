"""
Image to Image Generator API:
- Accepts one or more image URLs
- Downloads the images
- Extracts/crops bounding boxes from the images
- Returns all cropped images together

Run:
  pip install -r requirements.txt
  uvicorn app:app --host 0.0.0.0 --port 8000

API Usage:
  POST /crop-image
  
  Single image:
    {
      "image_url": "https://example.com/image.jpg",
      "use_detection": true,
      "detect_windows_only": true
    }
  
  Multiple images:
    {
      "image_urls": [
        "https://example.com/image1.jpg",
        "https://example.com/image2.jpg"
      ],
      "use_detection": true,
      "detect_windows_only": true
    }
  
  Manual bounding boxes:
    {
      "image_url": "https://example.com/image.jpg",
      "bounding_boxes": [
        {"x": 100, "y": 100, "width": 200, "height": 200, "label": "object1"}
      ]
    }
"""

import os
import uuid
import io
import shutil
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests
from PIL import Image
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

app = FastAPI(title="Image to Image Generator", version="1.1.0")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./cropped_images")).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class BoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    label: Optional[str] = None


class CropRequest(BaseModel):
    image_url: Optional[HttpUrl] = None  # Single image URL (for backward compatibility)
    image_urls: Optional[List[HttpUrl]] = None  # Multiple image URLs
    bounding_boxes: Optional[List[BoundingBox]] = None
    use_detection: bool = False
    detect_windows_only: bool = False
    confidence_threshold: float = 0.5
    clear_previous: bool = True  # Delete previous cropped images before processing
    
    def get_image_urls(self) -> List[str]:
        """Get list of image URLs from either image_url or image_urls field."""
        if self.image_urls:
            return [str(url) for url in self.image_urls]
        elif self.image_url:
            return [str(self.image_url)]
        else:
            raise ValueError("Either image_url or image_urls must be provided")


def download_image(url: str) -> Image.Image:
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        # Convert to RGB if necessary
        if image.mode != "RGB":
            image = image.convert("RGB")
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {e}")


def crop_bounding_box(image: Image.Image, bbox: BoundingBox) -> Image.Image:
    """Crop a bounding box from an image."""
    # Ensure coordinates are within image bounds
    x = max(0, bbox.x)
    y = max(0, bbox.y)
    width = min(bbox.width, image.width - x)
    height = min(bbox.height, image.height - y)
    
    if width <= 0 or height <= 0:
        raise HTTPException(status_code=400, detail=f"Invalid bounding box: {bbox}")
    
    return image.crop((x, y, x + width, y + height))


def detect_objects(image: Image.Image, confidence_threshold: float = 0.5, windows_only: bool = False) -> List[BoundingBox]:
    """
    Detect objects in image using YOLO or advanced window detection.
    If windows_only=True, uses advanced image processing to detect window frames.
    """
    # If windows_only, use advanced detection first
    if windows_only:
        bounding_boxes = detect_windows_advanced(image, confidence_threshold)
        # If advanced detection found windows, return them
        if bounding_boxes:
            return bounding_boxes
        # Otherwise, fall back to YOLO with filtering
    
    try:
        from ultralytics import YOLO
        
        # Load a pretrained YOLO model
        model = YOLO("yolov8n.pt")  # nano model for speed
        
        # Run inference
        results = model(image, conf=confidence_threshold)
        
        bounding_boxes = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x = int(x1)
                y = int(y1)
                width = int(x2 - x1)
                height = int(y2 - y1)
                
                # Get class label
                cls = int(box.cls[0])
                label = model.names[cls]
                
                # If windows_only, filter for rectangular objects that could be windows
                if windows_only:
                    aspect_ratio = width / height if height > 0 else 0
                    area = width * height
                    img_area = image.width * image.height
                    
                    # Filter for rectangular objects that could be windows
                    # Windows are typically rectangular and medium to large
                    if (0.3 <= aspect_ratio <= 3.0 and  # More flexible aspect ratio
                        area > img_area * 0.005 and      # At least 0.5% of image (smaller threshold)
                        area < img_area * 0.9):          # But not more than 90%
                        bounding_boxes.append(BoundingBox(
                            x=x, y=y, width=width, height=height, label="window"
                        ))
                else:
                    bounding_boxes.append(BoundingBox(
                        x=x, y=y, width=width, height=height, label=label
                    ))
        
        return bounding_boxes
    except ImportError:
        raise HTTPException(
            status_code=400,
            detail="YOLO not installed. Install with: pip install ultralytics"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Object detection failed: {e}")


def detect_windows_advanced(image: Image.Image, confidence_threshold: float = 0.5) -> List[BoundingBox]:
    """
    Advanced window detection using image processing techniques.
    Detects rectangular regions that could be windows using multiple methods.
    """
    try:
        import cv2
        import numpy as np
        
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Method 1: Edge detection and contour finding
        edges = cv2.Canny(gray, 30, 100, apertureSize=3)
        
        # Dilate edges to connect nearby edges
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        img_area = image.width * image.height
        min_area = img_area * 0.005  # At least 0.5% of image
        max_area = img_area * 0.9    # Max 90% of image
        
        # Method 2: HoughLines to detect rectangular structures
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
        
        # Process contours
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area <= area <= max_area:
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter for rectangular shapes (windows are typically rectangular)
                aspect_ratio = w / h if h > 0 else 0
                if 0.3 <= aspect_ratio <= 3.0:  # More flexible
                    # Check if it's roughly rectangular (contour approximation)
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    if len(approx) >= 4:  # At least 4 vertices (rectangular)
                        bounding_boxes.append(BoundingBox(
                            x=x, y=y, width=w, height=h, label="window"
                        ))
        
        # Remove overlapping/duplicate boxes
        bounding_boxes = remove_overlapping_boxes(bounding_boxes, overlap_threshold=0.5)
        
        return bounding_boxes
    except ImportError:
        # If OpenCV not available, return empty list
        return []
    except Exception as e:
        return []


def upload_to_cloud_storage(img_bytes: io.BytesIO, filename: str) -> str:
    """
    Upload image to cloud storage and return URL.
    Supports: ImgBB, Cloudinary, or returns base64 data URL as fallback.
    """
    img_bytes.seek(0)
    
    # Option 1: ImgBB (requires API key)
    imgbb_api_key = os.getenv("IMGBB_API_KEY", "")
    if imgbb_api_key:
        try:
            img_base64 = base64.b64encode(img_bytes.read()).decode()
            response = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": imgbb_api_key,
                    "image": img_base64,
                    "name": filename
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["data"]["url"]
        except Exception:
            pass
    
    # Option 2: Cloudinary
    cloudinary_cloud = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    if cloudinary_cloud:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=cloudinary_cloud,
                api_key=os.getenv("CLOUDINARY_API_KEY"),
                api_secret=os.getenv("CLOUDINARY_API_SECRET")
            )
            img_bytes.seek(0)
            result = cloudinary.uploader.upload(
                img_bytes,
                folder="cropped-images",
                public_id=filename.replace(".jpg", "")
            )
            return result["secure_url"]
        except Exception:
            pass
    
    # Option 3: Return base64 data URL (works but not ideal for large images)
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.read()).decode()
    return f"data:image/jpeg;base64,{img_base64}"


def remove_overlapping_boxes(boxes: List[BoundingBox], overlap_threshold: float = 0.5) -> List[BoundingBox]:
    """Remove overlapping bounding boxes, keeping the largest ones."""
    if not boxes:
        return boxes
    
    # Sort by area (largest first)
    boxes_with_area = [(box, box.width * box.height) for box in boxes]
    boxes_with_area.sort(key=lambda x: x[1], reverse=True)
    
    filtered = []
    for box, _ in boxes_with_area:
        is_overlapping = False
        for existing_box in filtered:
            # Calculate intersection over union (IoU)
            x1 = max(box.x, existing_box.x)
            y1 = max(box.y, existing_box.y)
            x2 = min(box.x + box.width, existing_box.x + existing_box.width)
            y2 = min(box.y + box.height, existing_box.y + existing_box.height)
            
            if x2 > x1 and y2 > y1:
                intersection = (x2 - x1) * (y2 - y1)
                area1 = box.width * box.height
                area2 = existing_box.width * existing_box.height
                union = area1 + area2 - intersection
                iou = intersection / union if union > 0 else 0
                
                if iou > overlap_threshold:
                    is_overlapping = True
                    break
        
        if not is_overlapping:
            filtered.append(box)
    
    return filtered


def process_single_image(
    image_url: str,
    request: CropRequest,
    job_dir: Path,
    image_index: int = 0
) -> tuple[List[Dict[str, Any]], List[str]]:
    """Process a single image and return saved files and errors."""
    saved_files: List[Dict[str, Any]] = []
    errors: List[str] = []
    
    # Download image
    try:
        image = download_image(image_url)
    except HTTPException:
        raise
    except Exception as e:
        errors.append(f"Failed to download image {image_index + 1} ({image_url}): {e}")
        return saved_files, errors
    
    # Get bounding boxes
    bounding_boxes = request.bounding_boxes
    
    if request.use_detection:
        try:
            bounding_boxes = detect_objects(
                image, 
                request.confidence_threshold,
                windows_only=request.detect_windows_only
            )
            if not bounding_boxes:
                errors.append(f"No objects detected in image {image_index + 1}" + (" (no windows found)" if request.detect_windows_only else ""))
                return saved_files, errors
        except HTTPException:
            raise
        except Exception as e:
            errors.append(f"Detection failed for image {image_index + 1}: {e}")
            if not request.bounding_boxes:
                return saved_files, errors
            bounding_boxes = request.bounding_boxes
    
    if not bounding_boxes:
        errors.append(f"No bounding boxes provided for image {image_index + 1} and detection not enabled")
        return saved_files, errors
    
    # Crop each bounding box (all windows will be cropped)
    window_count = 0
    for idx, bbox in enumerate(bounding_boxes):
        try:
            cropped = crop_bounding_box(image, bbox)
            
            # Generate filename - prioritize window naming
            label = bbox.label or f"crop_{idx+1}"
            if "window" in label.lower() or request.detect_windows_only:
                window_count += 1
                label = f"window_{window_count}"
            
            # Sanitize label for filename
            safe_label = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in label)
            # Include image index in filename if processing multiple images
            if image_index > 0:
                filename = f"img{image_index+1}_{idx+1:03d}_{safe_label}.jpg"
            else:
                filename = f"{idx+1:03d}_{safe_label}.jpg"
            out_path = job_dir / filename
            
            # Save cropped image to bytes
            img_bytes = io.BytesIO()
            cropped.save(img_bytes, format="JPEG", quality=95)
            img_bytes.seek(0)
            
            # Upload to cloud storage and get URL
            image_url_result = upload_to_cloud_storage(img_bytes, filename)
            
            # Also save locally for backup (optional - may fail on some platforms)
            try:
                # Ensure directory exists
                out_path.parent.mkdir(parents=True, exist_ok=True)
                # Save using string path (more reliable on Render)
                cropped.save(str(out_path), "JPEG", quality=95)
            except Exception as save_error:
                # If local save fails, continue anyway (cloud storage is primary)
                # Log the error but don't fail the request
                pass
            
            saved_files.append({
                "url": image_url_result,
                "path": str(out_path),
                "filename": filename,
                "label": label,
                "source_image": image_url,
                "image_index": image_index + 1,
                "dimensions": {
                    "width": cropped.width,
                    "height": cropped.height
                },
                "bbox": {
                    "x": bbox.x,
                    "y": bbox.y,
                    "width": bbox.width,
                    "height": bbox.height
                }
            })
        except Exception as e:
            errors.append(f"Failed to crop box {idx+1} from image {image_index + 1}: {e}")
    
    return saved_files, errors


@app.post("/crop-image")
async def crop_image(request: CropRequest = Body(...)) -> JSONResponse:
    """Crop bounding boxes from one or more image URLs. Detects and crops all windows if requested."""
    
    # Validate input
    try:
        image_urls = request.get_image_urls()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Clear previous cropped images if requested
    if request.clear_previous:
        try:
            if OUTPUT_DIR.exists():
                for item in OUTPUT_DIR.iterdir():
                    if item.is_dir():
                        shutil.rmtree(item)
                    elif item.is_file():
                        item.unlink()
        except Exception as e:
            # Log but don't fail if cleanup fails
            pass
    
    job_id = uuid.uuid4().hex
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    job_dir = OUTPUT_DIR / f"{ts}_{job_id}"
    job_dir.mkdir(parents=True, exist_ok=True)
    
    all_saved_files: List[Dict[str, Any]] = []
    all_errors: List[str] = []
    
    # Process each image
    for idx, image_url in enumerate(image_urls):
        try:
            saved_files, errors = process_single_image(image_url, request, job_dir, image_index=idx)
            all_saved_files.extend(saved_files)
            all_errors.extend(errors)
        except HTTPException:
            raise
        except Exception as e:
            all_errors.append(f"Failed to process image {idx + 1} ({image_url}): {e}")
    
    return JSONResponse({
        "status": "success",
        "job_id": job_id,
        "output_dir": str(job_dir),
        "images_processed": len(image_urls),
        "saved_count": len(all_saved_files),
        "saved_files": all_saved_files,
        "errors": all_errors,
    })


@app.get("/")
async def root():
    return {
        "message": "Image to Image Generator API",
        "endpoints": {
            "POST /crop-image": "Crop bounding boxes from one or more image URLs. Supports single image_url or multiple image_urls."
        },
        "usage": {
            "single_image": {
                "image_url": "https://example.com/image.jpg",
                "use_detection": True,
                "detect_windows_only": True
            },
            "multiple_images": {
                "image_urls": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "use_detection": True,
                "detect_windows_only": True
            }
        }
    }
