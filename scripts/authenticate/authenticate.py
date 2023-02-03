"""Script to provide the authentication object"""
import os
from azure.ai.ml import MLClient
from azure.identity import EnvironmentCredential
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential


def load_variables():
    """Load authentication details"""
    load_dotenv('./variables.env')
    auth_dict = {
            "subscription_id": os.environ['SUB_ID'],
            "resource_group": os.environ['RESOURCE_GROUP'],
            "workspace": os.environ['WORKSPACE_NAME'],
            "client_id": os.environ['AZURE_CLIENT_ID'], #hardcoded with EnvironmentCredential
            "tenant_id": os.environ['AZURE_TENANT_ID'], #hardcoded with EnvironmentCredential
            "client_secret": os.environ['AZURE_CLIENT_SECRET'], #hardcoded with EnvironmentCredential
            "location": os.environ['LOCATION'],
            "blob_container": os.environ['BLOB_CONTAINER'],
            "storage_key": os.environ['STORAGE_KEY'],
            "adls_account_name": os.environ['ADLS_ACCT_NAME'],
            "adls_datastore": os.environ['ADLS_DATASTORE'],
            "text_analytics_key": os.environ['TEXT_ANALYTICS_KEY'],
            "text_analytics_endpoint": os.environ['TEXT_ANALYTICS_ENDPOINT'],
            }
    return auth_dict


auth_var = load_variables()


ml_client = MLClient(credential=EnvironmentCredential(),
                     subscription_id=auth_var['subscription_id'],
                     resource_group_name=auth_var['resource_group'],
                     workspace_name=auth_var['workspace'],)
