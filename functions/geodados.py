
import os
import requests
import json
import sys
import time
import logging
from dotenv import load_dotenv

# Loading Environment Variables
load_dotenv()

LOGIN_NAME=os.getenv("GEODADOS_LOGIN")
LOGIN_PASSWORD=os.getenv("GEODADOS_PASSWORD")
TOKEN=os.getenv("GEODADOS_TOKEN")

headers = {
    'Authorization': f'Basic {TOKEN}'
}
auth = (LOGIN_NAME, LOGIN_PASSWORD)

def get_directory_path(file_path):
    """
    Get the directory path from the complete file path.

    Parameters:
    file_path (str): The complete file path.

    Returns:
    str: The directory path.
    """
    return os.path.dirname(file_path)

def check_extension(file_name, extension):
    """
    Check if the given file name has the specified extension.

    Parameters:
    file_name (str): The name of the file to check.
    extension (str): The extension to check for (with or without leading dot).

    Returns:
    bool: True if the file has the specified extension, False otherwise.
    """
    # Ensure the extension starts with a dot
    if not extension.startswith('.'):
        extension = '.' + extension

    # Check if the file name ends with the specified extension
    return file_name.lower().endswith(extension.lower())

def make_upload_to_geonode(file_name, file_path, metadata, style_path):
    url = "https://geodados.daee.sp.gov.br/api/v2/uploads/upload?overwrite_existing_layer=true&"
    path_without_file = get_directory_path(file_path)

    def open_file_safely(file_path, mode):
        try:
            return open(file_path, mode)
        except FileNotFoundError as e:
            logging.error(f"File not found: {file_path}")
            raise e
        except Exception as e:
            logging.error(f"Error opening file: {file_path}")
            raise e

    try:
        if check_extension(file_path, ".shp"):
            
            files = [
                ('base_file', (f"{file_name}.shp", open_file_safely(f"{path_without_file}/{file_name}.shp", 'rb'), 'application/octet-stream')),
                ('dbf_file', (f"{file_name}.dbf", open_file_safely(f"{path_without_file}/{file_name}.dbf", 'rb'), 'application/octet-stream')),
                ('shx_file', (f"{file_name}.shx", open_file_safely(f"{path_without_file}/{file_name}.shx", 'rb'), 'application/octet-stream')),
                ('prj_file', (f"{file_name}.prj", open_file_safely(f"{path_without_file}/{file_name}.prj", 'rb'), 'application/octet-stream')),
                ('sld_file', ('rainfall_daily_polygon.sld', open_file_safely(style_path, 'rb'), 'application/octet-stream'))
            ]
        elif check_extension(file_path, ".tif"):
            files = [
                ('base_file', (f"{file_name}.tif", open_file_safely(f"{path_without_file}/{file_name}.tif", 'rb'), 'application/octet-stream')),
                ('tif_file', (f"{file_name}.tif", open_file_safely(f"{path_without_file}/{file_name}.tif", 'rb'), 'application/octet-stream')),
                ('sld_file', ('rainfall_daily_raster.sld', open_file_safely(style_path, 'rb'), 'application/octet-stream'))
            ]
        else:
            logging.error("Invalid file extension to upload to Geonode. Try again")
            return

        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        logging.info("Response: %s", response.json())

        execution_id = response.json().get('execution_id')
        if not execution_id:
            logging.error("No execution ID found in the response.")
            return

        while True:
            exec_ret = requests.get(f"https://geodados.daee.sp.gov.br/api/v2/executionrequest/{execution_id}", headers=headers)
            exec_ret.raise_for_status()
            is_finished = exec_ret.json()['request'].get('finished')
            if is_finished:
                break
            logging.info("%s => Ret State of Upload File: %s", file_name, is_finished)
            time.sleep(1)

        dataset_id = exec_ret.json()['request']['output_params']['resources'][0]['id']
        response = requests.patch(f'https://geodados.daee.sp.gov.br/api/v2/datasets/{dataset_id}', auth=auth, json=metadata)
        response.raise_for_status()
        logging.info("Update Metadata of Dataset")

        return dataset_id

    except requests.RequestException as e:
        logging.error(f"HTTP request failed: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        for f in files:
            f[1][1].close()