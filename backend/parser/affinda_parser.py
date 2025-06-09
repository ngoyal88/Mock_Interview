import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AFFINDA_API_KEY")
API_URL = "https://api.affinda.com/v2/resumes"

def parse_resume(file_bytes: bytes, filename: str):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    files = {
        "file": (filename, file_bytes, "application/pdf")
    }

    response = requests.post(API_URL, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Affinda error: {response.status_code} - {response.text}")
