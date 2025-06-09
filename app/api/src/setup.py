import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_drive_service():

    credentials_path = os.getenv("GOOGLE_CREDENTIALS")
    if not credentials_path:
        raise ValueError("Missing GOOGLE_CREDENTIALS environment variable")
    
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Create credentials using the service account file
    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

    # Build the Google Drive service
    drive_service = build('drive', 'v3', credentials=credentials)
    return drive_service



