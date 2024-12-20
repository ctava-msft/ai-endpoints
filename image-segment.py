import concurrent.futures
import os
import requests
from PIL import Image
import numpy as np
import urllib.request
import json
import os
import ssl
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.


image_path = '26_OCT_retinal.png'
image = Image.open(image_path)

# Convert the image to a NumPy array
image_data = np.array(image)
# Convert the NumPy array to a list
image_data_list = image_data.tolist()


# Convert the image to bytes
buffered = BytesIO()
image.save(buffered, format="PNG")
image_bytes = buffered.getvalue()

# Encode the bytes to a base64 string
image_base64 = base64.b64encode(image_bytes).decode('utf-8')

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script
data = {
  "input_data": {
    "data": [
      [
        image_base64,
        "please segment this OCT image"
      ]
    ],
    "columns": [
      "image",
      "text"
    ],
    "index": [
      0
    ]
  }
}

body = str.encode(json.dumps(data))

url = 'https://christava-1459-lgmys.eastus.inference.ml.azure.com/score'
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
api_key = API_KEY
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url, body, headers)

def print_json_structure(data, indent=0):
    if isinstance(data, dict):
        for key, value in data.items():
            print(' ' * indent + str(key) + ': ' + str(type(value).__name__))
            print_json_structure(value, indent + 2)
    elif isinstance(data, list):
        print(' ' * indent + '[list of ' + str(len(data)) + ' items]')
        if len(data) > 0:
            print_json_structure(data[0], indent + 2)
    else:
        print(' ' * indent + str(type(data).__name__))

try:
    response = urllib.request.urlopen(req)
    # Assuming 'result' contains the JSON response with the base64 image string
    result = response.read()
    try:
        result_data = json.loads(result)
        #print(result_data.keys())
        #print_json_structure(result_data)
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        exit(1)

    #print(result_data[0])
    # Extract the base64 image string from the response
    image_base64 = result_data[0]['image_features']
    #print(type(image_base64))
    parsed_json = json.loads(image_base64)

    # Extract the base64-encoded image data
    image_base64 = parsed_json['data']

    print(type(image_base64))   
    # Print the first few characters of the base64 string for debugging
    print(image_base64[:100])

    print(f"Length of base64 string: {len(image_base64)}")

    # Ensure the base64 string is properly padded
    missing_padding = len(image_base64) % 4
    if missing_padding:
        image_base64 += '=' * (4 - missing_padding)

    print(result_data[0]['text_features'])
    # Decode the base64 string to bytes
    try:
        image_bytes = base64.b64decode(image_base64)
    except base64.binascii.Error as e:
        print(f"Base64 decoding error: {e}")
        exit(1)

    # Print the first few bytes of the decoded image data for debugging
    print(image_bytes[:100])

    # Save the decoded bytes to a file for debugging
    with open('debug_image.jpg', 'wb') as f:
        f.write(image_bytes)

    # Convert the bytes to an image
    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()  # Verify that it is, in fact, an image
    except (IOError, SyntaxError) as e:
        print(f"Image verification error: {e}")
        exit(1)

    # Convert the bytes to an image
    image = Image.open(BytesIO(image_bytes))

    # Save or display the image
    image.save('output_image.jpg')
    image.show()
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))
    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))