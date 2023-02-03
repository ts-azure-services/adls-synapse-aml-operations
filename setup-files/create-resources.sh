#!/bin/bash
grn=$'\e[1;32m'
end=$'\e[0m'

set -e

# Start of script
SECONDS=0
printf "${grn}Starting creation of Synapse, ADLS and AML infra resources...${end}\n"

# Source subscription ID, and prep config file
source sub.env
sub_id=$SUB_ID

# Set the default subscription 
az account set -s $sub_id

# Source unique name for RG, workspace creation
random_name_generator='/scripts/name-generator/random_name.py'
unique_name=$(python $PWD$random_name_generator)
number=$[ ( $RANDOM % 10000 ) + 1 ]
resourcegroup=$unique_name$number
workspacename=$unique_name$number'ws'
user_id='f1f01265-ed67-4304-97e9-a09ed422718d' # find user id object id
location='westus'
synapsews=$unique_name'synapsews'
storageacctname=$unique_name'storageacct'
container='reviews'
adls_datastore='customer_reviews_adls1'
filesharename='files'
sqluser='sqluser344'
sqlpw=$(uuidgen)
sparkpoolname='sppool'$number
textanalyticsservice=$unique_name'textanalytics'

# Create a resource group
printf "${grn}Starting creation of resource group...${end}\n"
rg_create=$(az group create --name $resourcegroup --location $location)
printf "Result of resource group create:\n $rg_create \n"

# Create an ADLS Gen 2 Storage account
printf "${grn}Starting creation of ADLS Gen 2...${end}\n"
ws_result=$(az storage account create \
  --name $storageacctname \
  -g $resourcegroup \
  --enable-hierarchical-namespace "true")
printf "Result of ADLS Gen 2 create:\n $ws_result \n"
sleep 10

# Create the blob container
storagecredentials=$(az storage account show-connection-string \
  --name $storageacctname \
  -g $resourcegroup \
  --query "connectionString"
)

printf "${grn}Creating the blob container...${end}\n"
blobContainerCreate=$(az storage container create --connection-string $storagecredentials --name $container)
printf "Result of blob container create:\n $blobContainerCreate \n"
sleep 2


# Getting storage account key
printf "${grn}Getting storage account key 1...${end}\n"
storageKey=$(az storage account keys list -g $resourcegroup -n $storageacctname --query "[0].value")
# printf "Result of storage account key retrieval:\n $storageKey \n"


# Create a Synapse workspace
printf "${grn}Starting creation of Synapse workspace...${end}\n"
ws_result=$(az synapse workspace create \
  --name $synapsews \
  -g $resourcegroup \
  --storage-account $storageacctname \
  --file-system $filesharename \
  --sql-admin-login-user $sqluser \
  --sql-admin-login-password $sqlpw \
  --location $location)
printf "Result of Synapse workspace create:\n $ws_result \n"
sleep 5

# Create AML workspace through CLI
printf "${grn}Starting creation of AML workspace...${end}\n"
ws_result=$(az ml workspace create -n $workspacename -g $resourcegroup)
printf "Result of workspace create:\n $ws_result \n"

# Create Synapse Spark pool
printf "${grn}Starting creation of Synapse Spark pool...${end}\n"
ws_result=$(az synapse spark pool create \
  --name $sparkpoolname \
  --node-count 3 \
  --node-size "Small" \
  -g $resourcegroup \
  --spark-version "2.4" \
  --workspace-name $synapsews)
printf "Result of Spark pool create:\n $ws_result \n"


# Create Synapse firewall rules
printf "${grn}Creating Synapse firewall rules...${end}\n"
result=$(az synapse workspace firewall-rule create \
  --name "noRestriction" \
  --workspace-name $synapsews \
  --resource-group $resourcegroup \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255)
printf "Result of Synapse firewall create:\n $result \n"
sleep 5

## Create text analytics resource 
printf "${grn}Creating the text analytics resource...${end}\n"
textanalyticsserviceCreate=$(az cognitiveservices account create \
	--name $textanalyticsservice \
	-g $resourcegroup \
	--kind 'TextAnalytics' \
	--sku S \
	--location $location \
	--yes)
printf "Result of text analytics create:\n $textanalyticsserviceCreate \n"

# Generate service principal credentials
printf "${grn}Generate service principal credentials...${end}\n"
credentials=$(az ad sp create-for-rbac --name "sp$resourcegroup" \
	--scopes /subscriptions/$sub_id/resourcegroups/$resourcegroup \
	--role Contributor)
sleep 10


# Capture credentials for 'jq' parsing
credFile='cred.json'
printf "$credentials" > $credFile
clientID=$(cat $credFile | jq '.appId')
clientSecret=$(cat $credFile | jq '.password')
tenantID=$(cat $credFile | jq '.tenant')
rm $credFile

# Remove double quotes from service principal variables
clientID=$(sed -e 's/^"//' -e 's/"$//' <<<"$clientID")
clientSecret=$(sed -e 's/^"//' -e 's/"$//' <<<"$clientSecret")
tenantID=$(sed -e 's/^"//' -e 's/"$//' <<<"$tenantID")

# Grant Storage Data Blob Contributor access to service principal
printf "${grn}Get service principal object id ...${end}\n"
object_id=$(az ad sp show --id $clientID --query "id")
object_id=$(sed -e 's/^"//' -e 's/"$//' <<<"$object_id")
sleep 2

printf "${grn}Assign Storage Data Blob contributor access to service principal...${end}\n"
result=$(az role assignment create \
  --assignee-object-id $object_id \
  --assignee-principal-type "ServicePrincipal" \
  --role "Storage Blob Data Contributor" \
  --resource-group $resourcegroup)
printf "Result of RBAC assignment to service principal:\n $result \n"

# Query for Synapse workspace object id, and then assign role
printf "${grn}Retrieve ID for Synapse workspace.......${end}\n"
synapse_id=$(az synapse workspace show --name $synapsews -g $resourcegroup --query "identity.principalId")
printf "Retrieved ID for Synapse WS:\n $result \n"
synapse_id=$(sed -e 's/^"//' -e 's/"$//' <<<"$synapse_id")
sleep 2

printf "${grn}Assign Storage Data Blob contributor access to Synapse workspace...${end}\n"
result=$(az role assignment create \
  --assignee $synapse_id \
  --role "Storage Blob Data Contributor" \
  --resource-group $resourcegroup)
printf "Result of RBAC assignment to Synapse WS:\n $result \n"

## Assign user to be able to write to Storage blob
printf "${grn}Assign Storage Data Blob contributor access to user...${end}\n"
result=$(az role assignment create \
  --assignee $user_id \
  --role "Storage Blob Data Contributor" \
  --resource-group $resourcegroup)
printf "Result of RBAC assignment for user:\n $result \n"

# Get Web URL for Synapse workspace
WorkspaceWeb=$(az synapse workspace show \
  --name $synapsews \
  -g $resourcegroup | jq -r '.connectivityEndpoints | .web')

WorkspaceDev=$(az synapse workspace show \
  --name $synapsews \
  -g $resourcegroup | jq -r '.connectivityEndpoints | .dev')


## Retrieve key from cognitive services
printf "${grn}Retrieve the keys and endpoint of the text analytics resource...${end}\n"
Key=$(az cognitiveservices account keys list -g $resourcegroup --name $textanalyticsservice --query "key1")
Endpoint=$(az cognitiveservices account show -g $resourcegroup --n $textanalyticsservice --query "properties.endpoint")

# Remove double-quotes in key
Key=$(sed -e 's/^"//' -e 's/"$//' <<<"$Key")

# Create variables file
printf "${grn}Writing out service principal variables...${end}\n"
env_variable_file='variables.env'
printf "AZURE_CLIENT_ID=$clientID \n" > $env_variable_file
printf "AZURE_CLIENT_SECRET=$clientSecret \n" >> $env_variable_file
printf "AZURE_TENANT_ID=$tenantID \n" >> $env_variable_file
printf "SUB_ID=$sub_id \n" >> $env_variable_file
printf "RESOURCE_GROUP=$resourcegroup \n" >> $env_variable_file
printf "WORKSPACE_NAME=$workspacename \n" >> $env_variable_file
printf "LOCATION=$location \n" >> $env_variable_file
printf "SYNAPSE_WS=$synapsews \n" >> $env_variable_file
printf "SYNAPSE_ID=$synapse_id \n" >> $env_variable_file
printf "ADLS_ACCT_NAME=$storageacctname \n" >> $env_variable_file
printf "ADLS_DATASTORE=$adls_datastore \n" >> $env_variable_file
printf "BLOB_CONTAINER=$container \n" >> $env_variable_file
printf "STORAGE_KEY=$storageKey \n" >> $env_variable_file
printf "FILE_SHARE_NAME=$filesharename \n" >> $env_variable_file
printf "SQLUSER=$sqluser \n" >> $env_variable_file
printf "SQLPW=$sqlpw \n" >> $env_variable_file
printf "WS_WEB=$WorkspaceWeb \n" >> $env_variable_file
printf "WS_DEV=$WorkspaceDev \n" >> $env_variable_file
printf "TEXT_ANALYTICS_RESOURCE=$textanalyticsservice \n" >> $env_variable_file
printf "TEXT_ANALYTICS_KEY=$Key \n" >> $env_variable_file
printf "TEXT_ANALYTICS_ENDPOINT=$Endpoint \n" >> $env_variable_file
