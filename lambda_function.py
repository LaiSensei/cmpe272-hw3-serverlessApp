import json
import base64
import os
import time
import urllib.request
from urllib.error import HTTPError
import boto3
import uuid

API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET_NAME")

s3_client = boto3.client("s3")


def generate_image(prompt, tags, max_retries=3, delay=10):
    full_prompt = f"{prompt} {', '.join(tags)}"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = json.dumps({"inputs": full_prompt}).encode("utf-8")

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                API_URL, data=data, headers=headers, method="POST"
            )
            with urllib.request.urlopen(req) as response:
                return response.read()
        except HTTPError as e:
            error_message = e.read().decode("utf-8")
            print(f"API Error: Status {e.code}, Message: {error_message}")
            if e.code == 503 and "is currently loading" in error_message:
                if attempt < max_retries - 1:
                    wait_time = delay * (attempt + 1)
                    print(f"Model is loading. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(
                        f"Model is still loading after {max_retries} attempts"
                    )
            else:
                raise Exception(f"API Error: {e.code} - {error_message}")
        except Exception as e:
            print(f"Request failed: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")

    raise Exception("Max retries reached")


def upload_to_s3(image_bytes):
    file_name = f"generated-images/{uuid.uuid4()}.png"
    s3_client.put_object(
        Bucket=S3_BUCKET, Key=file_name, Body=image_bytes, ContentType="image/png"
    )
    return f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"


def list_s3_images():
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix="generated-images/")
    images = []
    if "Contents" in response:
        for item in response["Contents"]:
            images.append(f"https://{S3_BUCKET}.s3.amazonaws.com/{item['Key']}")
    return images


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    try:
        # Check if the event is coming from API Gateway
        if "httpMethod" in event:
            if event["httpMethod"] == "GET":
                images = list_s3_images()
                return {
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "body": json.dumps({"images": images}),
                }
            elif event["httpMethod"] == "POST":
                body = (
                    json.loads(event["body"])
                    if isinstance(event["body"], str)
                    else event["body"]
                )
        else:
            # Direct invocation (like test events)
            body = (
                json.loads(event["body"])
                if isinstance(event["body"], str)
                else event["body"]
            )

        print(f"Parsed body: {json.dumps(body)}")

        prompt = body.get("prompt", "")
        tags = body.get("tags", [])

        if not prompt:
            raise ValueError("Prompt is required")

        image_bytes = generate_image(prompt, tags)
        image_url = upload_to_s3(image_bytes)
        all_images = list_s3_images()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"image_url": image_url, "all_images": all_images}),
        }
    except ValueError as ve:
        print(f"Validation error: {str(ve)}")
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(ve)}),
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }
