# Doc: https://learn.microsoft.com/en-us/python/api/mltable/mltable.mltable?view=azure-ml-py
import mltable
# from mltable import MLTableHeaders, MLTableFileEncoding
from azure.storage.blob import BlobClient
from azure.identity import DefaultAzureCredential
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../')))
from authenticate.authenticate import ml_client, auth_var

if __name__ == "__main__":
    # Define paths for specific outputs
    adls_datastore = auth_var['adls_datastore']
    delta_table_uri = "azureml://datastores/" + str(adls_datastore) + "/paths/customer-reviews/"
    my_path = {'folder': './'}

    tbl = mltable.from_delta_lake(
        # delta_table_uri=[my_path],
        delta_table_uri=delta_table_uri,
        timestamp_as_of='2023-01-15T00:00:00Z',
        # version_as_of=1.0,
        include_path_column=False,
    )

    # save the table to the local file system
    local_folder = "./setup-files"
    tbl.save(local_folder)

    # upload the MLTable file to your storage account
    storage_account_url = "https://" + str(auth_var['adls_account_name']) + ".blob.core.windows.net"
    container_name = auth_var['blob_container']  # "<filesystem>"
    data_folder_on_storage = 'customer-reviews'

    # get a blob client using default credential
    blob_client = BlobClient(
        credential=DefaultAzureCredential(),
        account_url=storage_account_url,
        container_name=container_name,
        blob_name=f'{data_folder_on_storage}/MLTable'
    )

    # upload to cloud storage
    with open(f'{local_folder}/MLTable', "rb") as mltable_file:
        blob_client.upload_blob(mltable_file)
