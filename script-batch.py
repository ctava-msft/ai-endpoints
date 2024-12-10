import concurrent.futures
import os
import requests

from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")

# Function to call Azure OpenAI endpoint
def call_azure_openai(note_batch):
    url = f"{ENDPOINT}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "notes": note_batch
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to break down notes into smaller batches
def batch_notes(notes, batch_size):
    for i in range(0, len(notes), batch_size):
        yield notes[i:i + batch_size]

# Main function to process notes in parallel
def process_notes_in_parallel(notes, batch_size):
    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_batch = {executor.submit(call_azure_openai, batch): batch for batch in batch_notes(notes, batch_size)}
        for future in concurrent.futures.as_completed(future_to_batch):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error processing batch: {e}")
    return results

# Example usage
if __name__ == "__main__":
    notes = ["note1", "note2", "note3", ..., "note3000"]  # Replace with your actual notes
    batch_size = 100  # Adjust batch size as needed
    results = process_notes_in_parallel(notes, batch_size)
    print(results)