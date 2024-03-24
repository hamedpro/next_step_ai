from re import I
from dotenv import load_dotenv
from kavenegar import *
import os
import requests
load_dotenv()
API_KEY = os.environ.get('SMS_PANEL_API_KEY')

# Recipient phone number
RECIPIENT = '09389980462'

# Message to send
MESSAGE = 'python is great'

# Kavenegar API endpoint
URL = 'https://api.kavenegar.com/v1/{api_key}/sms/send.json'.format(
    api_key=API_KEY)

# Request data
data = {
    'receptor': RECIPIENT,
    'message': MESSAGE,
}

# Set headers with your API key
headers = {'Authorization': f'ApiKey {API_KEY}'}

try:
    # Send POST request
    response = requests.post(URL, headers=headers, data=data)
    response.raise_for_status()  # Raise exception for non-200 status codes

    # Decode response (assuming JSON format)
    decoded_response = response.json()
    print(f"SMS Sent Successfully: {decoded_response}")
except requests.exceptions.RequestException as e:
    print(f"Error sending SMS: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
