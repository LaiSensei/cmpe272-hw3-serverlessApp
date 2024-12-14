# cmpe272-hw3-serverlessApp

This project is a serverless application that generates images based on user input using the Stable Diffusion model from Hugging Face. The generated images are stored in an S3 bucket and can be retrieved and displayed on a web page.

## Project Structure

### `lambda_function.py`

This file contains the AWS Lambda function that handles image generation and S3 interactions.

- **Functions:**
  - `generate_image(prompt, tags, max_retries=3, delay=10)`: Generates an image based on the provided prompt and tags.
  - `upload_to_s3(image_bytes)`: Uploads the generated image to the S3 bucket.
  - `list_s3_images()`: Lists all images stored in the S3 bucket.
  - `lambda_handler(event, context)`: The main handler function for the Lambda.

### `templates/index.html`

This file contains the HTML structure for the web page.

- **Elements:**
  - A textarea for entering the image description.
  - Checkboxes for selecting tags.
  - A button to generate the image.
  - A div to display the generated images.

### `static/script.js`

This file contains the JavaScript code for handling user interactions and API requests.

- **Functions:**
  - `displayImages(images)`: Displays the list of images on the web page.
  - `handleApiResponse(response)`: Handles the API response.
  - Event listeners for fetching and generating images.

### `static/styles.css`

This file contains the CSS styles for the web page.

- **Styles:**
  - Basic styling for the body, h1, textarea, checkboxes, button, and result div.

## Setup

1. Clone the repository.
2. Set up your AWS environment and configure the necessary environment variables:
   - `HUGGINGFACE_API_KEY`: Your Hugging Face API key.
   - `S3_BUCKET_NAME`: The name of your S3 bucket.

## Deployment

1. Deploy the Lambda function using AWS SAM or the AWS Management Console.
2. Ensure the S3 bucket is properly configured to store and serve images.

## Usage

1. Open `templates/index.html` in a web browser.
2. Enter a description for the image in the textarea.
3. Select any relevant tags.
4. Click the "Generate Image" button.
5. The generated image will be displayed on the web page.