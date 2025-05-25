import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from datetime import datetime
import pandas as pd
from tools import *
from autogluon.tabular import TabularPredictor
import zipfile
from dotenv import load_dotenv


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


def list_folder(parent_folder_id=None):
    results = get_drive_service().files().list(
        q=f"'{parent_folder_id}' in parents and trashed=false" if parent_folder_id else None,
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print("No folders or files found in Google Drive.")
    else:
        print("Folders and files in Google Drive:")
        for item in items:
            print(f"Name: {item['name']}, ID: {item['id']}, Type: {item['mimeType']}")


def list_files_in_root_only():
    q = "'root' in parents and trashed=false"

    results = get_drive_service().files().list(
        q=q,
        pageSize=1000,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    items = results.get('files', [])

    if not items:
        print("Brak plików w katalogu głównym.")
    else:
        print("Pliki w katalogu głównym (tylko ten poziom):")
        for item in items:
            print(f"Name: {item['name']}, ID: {item['id']}, Type: {item['mimeType']}")
    
def delete_file(file_or_folder_id):
    try:
        get_drive_service().files().delete(fileId=file_or_folder_id).execute()
        print(f"Successfully deleted file/folder with ID: {file_or_folder_id}")
    except Exception as e:
        print(f"Error deleting file/folder with ID: {file_or_folder_id}")
        print(f"Error details: {str(e)}")


def download_model():
    
    zip_file = 'tmp/tabular_model.zip'
    unzipped_dir = 'unzipped_model'

    model_id = None #pobiera najowszy model
    download_zip_file(suffix=model_id, folder_name='models', destination_path=zip_file, drive_service=get_drive_service())

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzipped_dir)

    print(f"Model rozpakowany do: {unzipped_dir}")

    loaded_predictor = TabularPredictor.load(unzipped_dir)
    print("Model został wczytany z ZIP-a!")
    print(loaded_predictor.model_best)

    #potem można to wykorzystac do predykcji np.
    #prediction = predictor.predict(input_df) -> zwraca ektykiety
    #probas = predictor.predict_proba(input_df) -> zwaraca prawdopodobieństwa etykiet


if __name__ == '__main__':

    load_dotenv()
    #operacje na google drive usług
    list_folder()
    download_model()


