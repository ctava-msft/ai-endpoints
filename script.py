import concurrent.futures
import os
import requests

from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")

# Function to call Azure OpenAI endpoint
def call_azure_openai(input):
    url = f"{ENDPOINT}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "input": input
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    input = "tell me a joke"
    results = call_azure_openai(input)
    print(results)