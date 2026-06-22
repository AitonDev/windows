import os
import json
import requests

PYTHON_API_URL = os.getenv("PYTHON_API_URL", "https://your-api.onrender.com")

def handler(req):
    try:
        # Handle OPTIONS
        if req.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }
        
        # Get body
        body = req.body
        if isinstance(body, str):
            data = json.loads(body)
        elif body:
            data = json.loads(body.decode('utf-8'))
        else:
            data = {}
        
        if 'image_url' not in data and 'image_urls' not in data:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({"error": "image_url or image_urls is required"})
            }
        
        payload = {
            "use_detection": data.get("use_detection", True),
            "detect_windows_only": data.get("detect_windows_only", True),
            "confidence_threshold": data.get("confidence_threshold", 0.3),
            "clear_previous": data.get("clear_previous", False),
            "batch_id": data.get("batch_id"),
            "pdf_id": data.get("pdf_id"),
            "pdf_name": data.get("pdf_name"),
            "page_number": data.get("page_number"),
            "source_image_index": data.get("source_image_index"),
            "source_label": data.get("source_label"),
        }
        if "image_url" in data:
            payload["image_url"] = data["image_url"]
        if "image_urls" in data:
            payload["image_urls"] = data["image_urls"]
        if "bounding_boxes" in data:
            payload["bounding_boxes"] = data["bounding_boxes"]
        
        # Call Python API
        resp = requests.post(
            f"{PYTHON_API_URL}/crop-image",
            json=payload,
            timeout=60
        )
        
        return {
            'statusCode': resp.status_code,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': resp.text
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({"error": str(e)})
        }
