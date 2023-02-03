import argparse
from azure.ai.ml.entities import Environment
import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '../')))
from authenticate.authenticate import ml_client

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", default="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04", type=str)
    parser.add_argument("-cf", "--conda_file", default="./setup-files/conda.yaml", type=str)
    parser.add_argument("-n", "--name", default="base-env", type=str)
    parser.add_argument("-v", "--version", type=str)
    parser.add_argument("-d", "--description", default="Env created from a Docker image + Conda env", type=str)
    args = parser.parse_args()

    try:
        env_docker_conda = Environment(
                image=args.image,
                conda_file=args.conda_file,
                name=args.name,
                version=args.version,
                description=args.description
                )
        ml_client.environments.create_or_update(env_docker_conda)
    except Exception as e:
        print(f"Error: {e}")
