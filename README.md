# Image to Image Generator API

A FastAPI service that downloads images from URLs and crops bounding boxes from them. Supports both manual bounding box coordinates and automatic object detection using YOLO.

## Features

- Download images from URLs
- Crop bounding boxes manually (provide coordinates)
- Automatic object detection using YOLO
- Save cropped images to local directory
- Returns JSON with paths to all cropped images

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The `ultralytics` package (YOLO) will download the model weights on first use (~6MB).

### 2. Run the Server

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoint

### POST `/crop-image`

Crops bounding boxes from an image URL.

**Request Body (JSON):**

**Option 1: Manual Bounding Boxes**
```json
{
  "image_url": "https://example.com/image.jpg",
  "bounding_boxes": [
    {
      "x": 100,
      "y": 100,
      "width": 200,
      "height": 200,
      "label": "object1"
    },
    {
      "x": 300,
      "y": 150,
      "width": 150,
      "height": 150,
      "label": "object2"
    }
  ]
}
```

**Option 2: Automatic Object Detection**
```json
{
  "image_url": "https://example.com/image.jpg",
  "use_detection": true,
  "confidence_threshold": 0.5
}
```

**Parameters:**
- `image_url` (required): URL of the image to download
- `bounding_boxes` (optional): List of bounding boxes with x, y, width, height, and optional label
- `use_detection` (optional, default: false): Use YOLO to automatically detect objects
- `confidence_threshold` (optional, default: 0.5): Confidence threshold for object detection (0.0-1.0)

**Response:**
```json
{
  "status": "success",
  "job_id": "abc123...",
  "output_dir": "/path/to/cropped_images/20250101_120000_abc123",
  "saved_count": 2,
  "saved_files": [
    {
      "path": "/path/to/cropped_images/.../001_object1.jpg",
      "filename": "001_object1.jpg",
      "label": "object1",
      "bbox": {
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 200
      }
    },
    ...
  ],
  "errors": []
}
```

## Usage Examples

### Using curl

**Manual bounding boxes:**
```bash
curl -X POST "http://localhost:8000/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "bounding_boxes": [
      {"x": 100, "y": 100, "width": 200, "height": 200, "label": "crop1"}
    ]
  }' | python3 -m json.tool
```

**Automatic detection:**
```bash
curl -X POST "http://localhost:8000/crop-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.jpg",
    "use_detection": true,
    "confidence_threshold": 0.5
  }' | python3 -m json.tool
```

### Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/crop-image",
    json={
        "image_url": "https://example.com/image.jpg",
        "use_detection": True,
        "confidence_threshold": 0.5
    }
)

result = response.json()
print(f"Found {result['saved_count']} objects")
for file_info in result['saved_files']:
    print(f"Saved: {file_info['path']}")
```

## n8n Integration

In your n8n HTTP Request node:

- **Method**: `POST`
- **URL**: `http://YOUR_SERVER:8000/crop-image`
- **Send Body**: `JSON`
- **Body**:
```json
{
  "image_url": "{{ $json.image_url }}",
  "use_detection": true,
  "confidence_threshold": 0.5
}
```

## Notes

- Images are saved in `./cropped_images/` by default (or `OUTPUT_DIR` env var)
- Each job creates a timestamped folder: `YYYYMMDD_HHMMSS_jobid/`
- Cropped images are saved as JPEG with quality 95
- YOLO model (yolov8n.pt) is downloaded automatically on first use
- Object detection supports 80 COCO classes (person, car, dog, etc.)
