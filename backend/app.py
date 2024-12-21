import os
import logging
from flask import Flask, request, jsonify
import requests
import boto3
from botocore.exceptions import NoCredentialsError
from urllib.parse import urlparse, unquote
from pathlib import Path
from dotenv import load_dotenv
from flask_cors import CORS
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)

# AWS Configuration
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

# Initialize boto3 S3 client
s3_client = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# Function to generate a valid file name from the URL


def generate_file_name_from_url(url):
    # Parse the URL to get the path
    parsed_url = urlparse(url)

    # Get the last part of the URL path
    file_name = os.path.basename(parsed_url.path)

    # If there's no file name, use the base of the URL or default name
    if not file_name:
        file_name = "file_from_url"

    # Decode URL to handle any encoded characters
    file_name = unquote(file_name)

    # Make sure the file name is valid (e.g., remove special characters, spaces, etc.)
    # This ensures only valid characters are kept
    file_name = Path(file_name).name

    return file_name


@app.route('/upload', methods=['POST'])
def upload_file():
    data = request.get_json()
    url = data.get('url')

    if not url:
        logging.error('No URL provided in the request body.')
        return jsonify({'error': 'URL is required'}), 400

    # Log received URL
    logging.info(f'Received URL: {url}')

    try:
        # Fetch the file from the URL
        response = requests.get(url, stream=True)

        if response.status_code != 200:
            logging.error(f'Failed fetch Status code: {response.status_code}')
            return jsonify({'error': 'Failed to fetch file from URL'}), 500

        logging.info('File fetched successfully from URL.')

        # Generate the file name based on the URL
        file_name = generate_file_name_from_url(url)
        logging.info(f'File name generated: {file_name}')

        # Upload file to S3
        try:
            s3_client.upload_fileobj(response.raw, S3_BUCKET_NAME, file_name)
            file_url = f'https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}'
            return jsonify({'s3Url': file_url}), 200

        except NoCredentialsError:
            logging.error('AWS credentials not found.')
            return jsonify({'error': 'AWS credentials not found'}), 500

    except requests.RequestException as e:
        logging.error(f'Error fetching file from URL: {e}')
        return jsonify({'error': 'Error fetching file from URL', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
