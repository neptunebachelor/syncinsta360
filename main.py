# Main entry point for the Insta360 Sync application.
import configparser
import logging
import os
import platform
import sys
from pathlib import Path
import time
import threading # Added for callback event handling
import requests # Added for HTTP file downloads
from tqdm import tqdm # Added for progress bar

from wifi_manager import WifiManager
from insta360_api.insta360 import camera # Corrected: Import the 'camera' class

# Protobuf message codes, for callback handling
from insta360_api.pb2 import get_file_list_pb2

class Insta360CallbackHandler:
    """
    A callback handler for the Insta360 camera API to process asynchronous responses.
    """
    def __init__(self, logger):
        self.logger = logger
        self.file_list_response = None
        self.event = threading.Event()
        self.file_list_lock = threading.Lock() # To protect file_list_response

    def __call__(self, message_dict):
        """
        This method is called by the camera API's receive thread with parsed messages.
        """
        response_code = message_dict.get('response_code')
        message_code = message_dict.get('message_code')

        if response_code == camera.RESPONSE_CODE_OK:
            if message_code == camera.PHONE_COMMAND_GET_FILE_LIST:
                self.logger.debug(f"Received GetFileList response: {message_dict}")
                with self.file_list_lock:
                    self.file_list_response = message_dict
                self.event.set() # Signal that the file list has arrived
            else:
                self.logger.debug(f"Received unhandled OK response for message code: {message_code}")
        elif response_code == camera.RESPONSE_CODE_ERROR:
            self.logger.error(f"Received ERROR response for message code {message_code}: {message_dict}")
            self.event.set() # Signal even on error to unblock main thread
        else:
            self.logger.debug(f"Received non-OK/ERROR response: {message_dict}")

def _sync_files(insta360_client, dest_dir, logger, camera_ip, callback_handler, delete_after_download):
    """
    Synchronizes files from Insta360 camera to the local destination directory.
    """
    logger.info("Requesting remote file list from camera...")
    try:
        # Clear any previous event and response
        callback_handler.event.clear()
        with callback_handler.file_list_lock:
            callback_handler.file_list_response = None

        insta360_client.GetCameraFilesList()
        
        # Wait for the file list response for up to 30 seconds
        if not callback_handler.event.wait(timeout=30):
            logger.error("Timeout waiting for file list from camera.")
            return False
        
        with callback_handler.file_list_lock:
            file_list_data = callback_handler.file_list_response
        
        if not file_list_data or file_list_data.get('response_code') != camera.RESPONSE_CODE_OK:
            logger.error("Failed to retrieve file list or received error response.")
            return False

        remote_uris = file_list_data.get('uri', [])
        total_remote_count = file_list_data.get('total_count', 0)
        
        logger.info(f"Received {len(remote_uris)} URIs from camera (Total count: {total_remote_count}).")
        
        # We assume URIs are relative paths like DCIM/Camera01/filename.mp4
        # Need to extract just the filename for local comparison
        remote_files_map = {} # map filename to full URI
        for uri in remote_uris:
            filename = Path(uri).name
            if filename: # Ensure it's not empty
                remote_files_map[filename] = uri
        
        logger.info(f"Identified {len(remote_files_map)} unique files from URIs on the camera.")
        
    except Exception as e:
        logger.error(f"Error during file list request: {e}")
        return False

    logger.info(f"Scanning local directory: {dest_dir} for existing files...")
    local_files = {f for f in os.listdir(dest_dir) if (dest_dir / f).is_file()}
    logger.info(f"Found {len(local_files)} files in local directory.")

    files_to_download = {}
    for filename, remote_uri in remote_files_map.items():
        if filename not in local_files:
            files_to_download[filename] = remote_uri
    
    if not files_to_download:
        logger.info("No new files to download. Local directory is up to date.")
        return True

    logger.info(f"Found {len(files_to_download)} new files to download.")
    
    # Calculate total size for progress bar if possible, otherwise use unknown size
    # This might require making HEAD requests, which adds overhead.
    # For now, we'll just show progress per file.
    
    download_count = 0
    for file_name, remote_uri in tqdm(files_to_download.items(), desc="Downloading files"):
        # Construct full download URL (assuming standard camera web server structure)
        download_url = f"http://{camera_ip}/{remote_uri}"
        local_file_path = dest_dir / file_name
        
        logger.info(f"Downloading {file_name} from {download_url}...")
        try:
            with requests.get(download_url, stream=True, timeout=10) as r:
                r.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                total_size = int(r.headers.get('content-length', 0))
                
                with open(local_file_path, 'wb') as f:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=file_name, leave=False) as pbar:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                            pbar.update(len(chunk))
                logger.info(f"Successfully downloaded {file_name}.")
                download_count += 1

            if delete_after_download:
                # TODO: Implement robust verification before deletion.
                # E.g., hash check, file size check.
                logger.warning(f"Deletion is enabled but not fully implemented with verification. Skipping deletion for {file_name}.")
                # try:
                #     insta360_client.DeleteCameraFile(remote_uri) # Assuming such a method exists/will be implemented
                #     logger.info(f"Deleted {file_name} from camera.")
                # except Exception as del_e:
                #     logger.error(f"Failed to delete {file_name} from camera: {del_e}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download {file_name} (HTTP request error): {e}")
        except Exception as e:
            logger.error(f"Failed to download {file_name} (General error): {e}")
            
    logger.info(f"Synchronization complete. Downloaded {download_count} new files.")
    return True

def main():
    """Main function to run the sync process."""
    
    # --- 1. Initialization ---
    config = configparser.ConfigParser()
    # Use an absolute path for config.ini to run from any directory
    config_path = Path(__file__).parent / 'config.ini'
    config.read(config_path)
    
    # Setup logging
    log_file = config.get('Logging', 'log_file', fallback='insta360_sync.log')
    log_level = config.get('Logging', 'log_level', fallback='INFO')
    logger = setup_logging(log_file, log_level)
    
    logger.info("--- Starting Insta360 Sync ---")
    
    # Check destination directory
    dest_dir = Path(config.get('Storage', 'destination_dir'))
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Backup destination: {dest_dir}")
    except OSError as e:
        logger.error(f"Error creating destination directory {dest_dir}: {e}")
        sys.exit(1)

    insta360_client = None # Initialize client as None
    delete_after_download = config.getboolean('Sync', 'delete_after_download', fallback=False)
    insta360_callback_handler = None # Initialize callback handler

    try:
        # --- 2. Connection Phase ---
        logger.info("Starting Wi-Fi connection phase...")
        wifi_manager = WifiManager(logger)
        
        ssid_prefixes = [p.strip() for p in config.get('Camera', 'ssid_prefix').split(',')]
        camera_ip = config.get('Camera', 'camera_ip')

        connection_successful = wifi_manager.find_and_connect(ssid_prefixes)
        
        if not connection_successful:
            logger.error("Could not connect to camera Wi-Fi. Aborting.")
            sys.exit(1)
            
        logger.info("Attempting to connect to Insta360 camera API...")
        insta360_callback_handler = Insta360CallbackHandler(logger)
        insta360_client = camera(camera_ip, logger, callback=insta360_callback_handler) # Pass callback handler
        
        api_connected = False
        for i in range(5): # Retry API connection a few times
            try:
                insta360_client.Open()
                api_connected = True
                logger.info("Successfully connected to Insta360 API.")
                break
            except Exception as e:
                logger.warning(f"Attempt {i+1}: Failed to connect to Insta360 API: {e}")
                time.sleep(2) # Wait before retrying
        
        if not api_connected:
            logger.error("Failed to connect to Insta360 API after multiple attempts. Aborting.")
            sys.exit(1)
        
        # --- 3. Synchronization Phase ---
        logger.info("Starting synchronization phase...")
        # Call the new _sync_files function
        _sync_files(insta360_client, dest_dir, logger, camera_ip, insta360_callback_handler, delete_after_download)
        
    finally:
        # --- 4. Cleanup Phase ---
        logger.info("Starting cleanup phase...")
        if insta360_client:
            try:
                insta360_client.Close()
                logger.info("Insta360 API disconnected.")
            except Exception as e:
                logger.error(f"Error disconnecting Insta360 API: {e}")
        
        wifi_manager.disconnect()
        
        logger.info("--- Insta360 Sync finished ---")


if __name__ == "__main__":
    main()
