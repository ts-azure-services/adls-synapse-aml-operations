# from azure.ai.ml.entities import Data
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml import command, dsl, Input, Output
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../../')))
from authenticate.authenticate import ml_client, auth_var

# Define paths for specific outputs
adls_datastore = auth_var['adls_datastore']
env = "base-env:1"
sentiment_outputs = "azureml://datastores/" + str(adls_datastore) + "/paths/sentiment-results/"
clustering_outputs = "azureml://datastores/" + str(adls_datastore) + "/paths/clustering-results/"

# Defining pipeline components
sentiment_component = command(
    code="./",
    inputs={"input_data": Input(type=AssetTypes.URI_FOLDER)},
    outputs={"output_data": Output(type=AssetTypes.URI_FOLDER)},  # , path=sentiment_outputs)},
    command="python ./scripts/aml-operations/pipeline/sentiment.py --input_data ${{inputs.input_data}} --output_data ${{outputs.output_data}}",
    environment=env,
    compute="cpu-cluster",
)

# Second component is to just print out the list of files
clustering_component = command(
    code="./",
    inputs={"input_data": Input(type=AssetTypes.URI_FOLDER)},
    outputs={"output_data": Output(type=AssetTypes.URI_FOLDER)},
    command="python ./scripts/aml-operations/pipeline/clustering.py --input_data ${{inputs.input_data}} --output_data ${{outputs.output_data}}",
    environment=env,
    compute="cpu-cluster",
)

# DEFINE THE PIPELINE
@dsl.pipeline(compute='cpu-cluster')
def seq_pipeline(input_pathway):
    # using data_prep_function like a python call with its own inputs
    sentiment_job = sentiment_component(input_data=input_pathway,)

    clustering_job = clustering_component(input_data=sentiment_job.outputs.output_data)

    # a pipeline returns a dictionary of outputs
    # keys will code for the pipeline output identifier
    return {
        "pipeline_sentiment_job": sentiment_job.outputs.output_data,
        "pipeline_clustering_output": clustering_job.outputs.output_data,
    }


if __name__ == "__main__":
    # INSTANTIATE THE PIPELINE
    # input_pathway = "azureml://datastores/" + str(adls_datastore) + "/paths/customer-reviews/"
    input_pathway = "azureml://subscriptions/" + str(auth_var['subscription_id']) + \
            "/resourcegroups/" + str(auth_var['resource_group']) + \
            "/workspaces/" + str(auth_var['workspace']) + \
            "/datastores/" + str(auth_var['adls_datastore']) + \
            "/paths/customer-reviews"
    pipeline = seq_pipeline(input_pathway=Input(type=AssetTypes.URI_FOLDER, path=input_pathway))
    pipeline.outputs.pipeline_sentiment_job = Output(type=AssetTypes.URI_FOLDER, path=sentiment_outputs)
    pipeline.outputs.pipeline_clustering_output = Output(type=AssetTypes.URI_FOLDER, path=clustering_outputs)

    # SUBMIT THE PIPELINE JOB
    pipeline_job = ml_client.jobs.create_or_update(pipeline, experiment_name="sequential-pipeline")
