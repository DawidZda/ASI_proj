import os
import zipfile
from autogluon.tabular import TabularPredictor
from tools import download_zip_file
from .setup import get_drive_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_predictor():
   
    model_id = os.getenv("MODEL_ID")

    logger.info(f"Model id: {model_id}")

    os.makedirs('model', exist_ok=True)

    zip_file = 'model/tabular_model.zip'

    unzipped_dir = 'unzipped_model'

    download_zip_file(suffix=model_id, folder_name='models', destination_path=zip_file, drive_service=get_drive_service())

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(unzipped_dir)

    logger.info(f"Model rozpakowany do: {unzipped_dir}")

    loaded_predictor = TabularPredictor.load(unzipped_dir)
    logger.info("Model został wczytany z ZIP-a!")

    return loaded_predictor
