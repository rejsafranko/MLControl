import os
import sys
import click
import subprocess
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from tqdm import tqdm
from mlcontrol.Services import Services
from mlcontrol.Exceptions import SubdirectoryNotFoundError

SERVICES = Services()


@click.group()
def mlcontrol():
    pass


@click.command()
@click.argument("project_name")
def init(project_name: str) -> None:
    """Initialize a new MLOps project on Google Drive."""
    click.echo(f"Initializing new MLOps project: {project_name}")
    service = SERVICES.authenticate()
    project_id = SERVICES.create_directory(service, project_name)  # Root directory.
    SERVICES.create_directory(service, "data", project_id)  # Subdirectory.
    SERVICES.create_directory(service, "models", project_id)  # Subdirectory.
    click.echo(f"Project {project_name} created with ID: {project_id}")


@click.command()
@click.argument("local_directory")
@click.argument("project_name")
def upload(local_directory: str, project_name: str) -> None:
    """Upload a local data directory to Google Drive."""
    click.echo(f"Uploading data to: {project_name}")
    sys.stdout.flush()
    service = SERVICES.authenticate()
    try:
        project_id = SERVICES.find_folder_by_name(service, project_name)
        data_folder_id = SERVICES.find_folder_by_name(
            service, "data", parent_id=project_id
        )
        dataset_name = SERVICES.parse_dataset_name(local_directory)
        dataset_folder_id = SERVICES.create_directory(
            service, dataset_name, data_folder_id
        )
    except ValueError as e:
        click.echo(f"Error: {e}")
        return
    except googleapiclient.errors.HttpError as e:
        click.echo(f"Google Drive API Error: {e}")
        return

    try:
        for root, dirs, files in os.walk(local_directory):
            files_list = list(files)
            for filename in SERVICES.custom_progress_bar(
                files_list, prefix="Uploading images: ", size=len(files_list)
            ):
                file_path = os.path.join(root, filename)
                file_metadata = {"name": filename, "parents": [dataset_folder_id]}
                media = MediaFileUpload(file_path, resumable=True)
                service.files().create(
                    body=file_metadata, media_body=media, fields="id"
                ).execute()
                sys.stdout.flush()  # Ensure the progress bar updates

        click.echo(
            f"Data from {local_directory} uploaded to Drive folder '{project_name}'."
        )

    except Exception as e:
        click.echo(f"Error uploading data: {e}")


@click.command()
@click.argument("project_name")
@click.option("-d", "folder_type", flag_value="data", help="List datasets.")
@click.option("-m", "folder_type", flag_value="models", help="List models.")
def list(project_name: str, folder_type: str) -> None:
    """List datasets for a selected project."""
    if not folder_type:
        click.echo("Please specify either -d for data or -m for models.")
        return
    service = SERVICES.authenticate()
    click.echo(f"Listing data for the {project_name} project:")
    try:
        project_id = SERVICES.find_folder_by_name(service, project_name)
        data_folder_id = SERVICES.find_folder_by_name(
            service, folder_type, parent_id=project_id
        )
        subdirectories = SERVICES.list_folders(service, data_folder_id)
        if not subdirectories:
            raise SubdirectoryNotFoundError(
                f"No {folder_type} found in '{project_name}'."
            )
        for subdirectory in subdirectories:
            click.echo(f"- {subdirectory['name']}")
    except ValueError as e:
        click.echo(f"Error: {e}")
    except SubdirectoryNotFoundError as e:
        click.echo(f"Error: {e}")  # Handle the custom exception
    except googleapiclient.errors.HttpError as e:
        click.echo(f"Google Drive API Error: {e}")


@click.command()
@click.option("--help", "help", flag_value=True)
def gpus(help) -> None:
    """Lists available GPUs provided by Vast.ai cloud service."""
    command = "vastai search offers"
    if help:
        click.echo(
            """
disk_space: float       disk storage space, in GB
gpu_arch: string        host machine gpu architecture (e.g. nvidia, amd)
gpu_ram: float          per GPU RAM in GB
rentable: bool          is the instance currently rentable
verified: bool          is the machine verified
            """
        )
        return
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()


mlcontrol.add_command(init)
mlcontrol.add_command(upload)
mlcontrol.add_command(list)
mlcontrol.add_command(gpus)


def print_banner():
    print(
        """
    __  _____    ______            __             __
   /  |/  / /   / ____/___  ____  / /__________  / /
  / /|_/ / /   / /   / __ \/ __ \/ __/ ___/ __ \/ / 
 / /  / / /___/ /___/ /_/ / / / / /_/ /  / /_/ / /  
/_/  /_/_____/\____/\____/_/ /_/\__/_/   \____/_/   
                                                   
CLI tool for MLOps tasks. 
        """
    )


def main():
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "mlcontrol"):
        print_banner()
    mlcontrol()


if __name__ == "__main__":
    main()
