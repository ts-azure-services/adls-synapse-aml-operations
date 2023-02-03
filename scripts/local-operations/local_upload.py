import os
from azure.storage.filedatalake import DataLakeServiceClient
# from azure.core._match_conditions import MatchConditions
# from azure.storage.filedatalake._models import ContentSettings
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../')))
from authenticate.authenticate import auth_var


def initialize_storage_account(storage_account_name, storage_account_key):
    """Initialize connection to storage account"""
    try:
        global service_client
        service_client = DataLakeServiceClient(
                account_url="{}://{}.dfs.core.windows.net".format("https", storage_account_name),
                credential=storage_account_key)
    except Exception as e:
        print(e)


def get_file_list(pathway=None):
    """File parsing logic"""
    file_paths = []
    for root, _, filenames in os.walk(pathway):
        for filename in filenames:
            # if ".csv" in filename:
            if ".parquet" in filename:
                file_paths.append(os.path.join(root, filename))
    return file_paths


def upload_file_to_directory_bulk(filepath=None, blob_container=None):
    """Upload file to directory"""
    try:
        file_system_client = service_client.get_file_system_client(file_system=blob_container)
        directory_client = file_system_client.get_directory_client("listings")
        file_client = directory_client.get_file_client(filepath.split('/')[-1:][0])
        with open(filepath, 'rb') as f:
            data = f.read()
        file_client.upload_data(data, overwrite=True)
    except Exception as e:
        print(e)


def main():

    # Initialize connection to storage account
    initialize_storage_account(
            storage_account_name=auth_var['adls_account_name'],
            storage_account_key=auth_var['storage_key'],
            )

    # Cycle through files created
    filepaths = get_file_list(pathway='./generated-data/')
    blob_container = auth_var['blob_container']
    # print(filepaths)
    for filepath in filepaths:
        upload_file_to_directory_bulk(filepath, blob_container)
        print(f"Uploaded: {filepath}")


if __name__ == "__main__":
    main()
