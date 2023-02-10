install:
	#conda create -n synapseops python=3.8 -y; conda activate synapseops
	pip install -r requirements.txt
	# pip install python-dotenv
	# pip install Faker
	# pip install pandas
	# pip install azure-storage-file-datalake
	# pip install scikit-learn
	# pip install azure-ai-ml
	# pip install azure-identity
	# pip install azure-ai-textanalytics
	# pip install mltable
	# pip install flake8

# Setup infrastructure
infra:
	./setup-files/create-resources.sh

# Generate sample data
gen_samples:
	rm -rf ./generated-data/
	python ./scripts/local-operations/local_samples.py

# Upload sample data to ADLS
upload_samples:
	python ./scripts/local-operations/local_upload.py

# Open a Synapse workspace, navigate to 'Data' and Linked sources
# Open a notebook on one of the parquet files in the 'listings' file path
# Manually use the commands in the synapse_delta.py file in the synapse-operations folder to convert parquet
# to delta

# Register a datastore to the ADLS Gen 2 in AML 
create_datastore:
	python ./scripts/aml-operations/register_datastore.py

# Setup a cluster in AML 
create_cluster:
	python ./scripts/aml-operations/cluster.py

# Setup an environment in AML 
create_env:
	python ./scripts/aml-operations/env.py

## Upload ML Table to the delta lake path 
# Confirm this by ensuring the MLTable is in the root of the delta table file path
upload_mltable:
	python ./scripts/aml-operations/upload_mltable.py

## Run AML pipeline for sentiment, and clustering
# Two outputs:
# sentiment-results, output of first pipeline step
# clustering-results, output of second pipeline step
local_run:
	python ./scripts/aml-operations/pipeline/pipeline.py
