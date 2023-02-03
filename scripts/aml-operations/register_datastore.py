from azure.ai.ml.entities import AzureDataLakeGen2Datastore
from azure.ai.ml.entities import ServicePrincipalConfiguration
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../')))
from authenticate.authenticate import auth_var, ml_client


if __name__ == "__main__":

    store = AzureDataLakeGen2Datastore(
            name=auth_var['adls_datastore'],
            description="Datastore pointing to an ADLS Gen 2 for customer reviews",
            account_name=auth_var['adls_account_name'],
            filesystem=auth_var['blob_container'],
            credentials=ServicePrincipalConfiguration(
                tenant_id=auth_var['tenant_id'],
                client_id=auth_var['client_id'],
                client_secret=auth_var['client_secret'])
            )

    ml_client.create_or_update(store)
