import os
import click
import subprocess
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

from mlcontrol.Services import Services

SERVICES = Services()


@click.group()
def mlcontrol():
    """CLI tool for MLOps tasks."""
    pass


def create_project(project_name: str) -> None:
    service = SERVICES.authenticate()
    project_id = SERVICES.create_directory(service, project_name)  # Root directory.
    SERVICES.create_directory(service, "data", project_id)  # Subdirectory.
    SERVICES.create_directory(service, "models", project_id)  # Subdirectory.
    click.echo(f"Project {project_name} created with ID: {project_id}")


@click.command()
@click.argument("project_name")
def init(project_name: str) -> None:
    """Initialize a new MLOps project on Google Drive."""
    click.echo(f"Initializing new MLOps project: {project_name}")
    create_project(project_name)


def upload_data(local_directory: str, drive_directory_name: str) -> None:
    service = SERVICES.authenticate()

    try:
        drive_directory_id = SERVICES.find_folder_by_name(service, drive_directory_name)
    except ValueError as e:
        click.echo(f"Error: {e}")
        return
    except googleapiclient.errors.HttpError as e:
        click.echo(f"Google Drive API Error: {e}")
        return

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_metadata = {"name": filename, "parents": [drive_directory_id]}
            media = MediaFileUpload(file_path, resumable=True)
            service.files().create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()

    click.echo(
        f"Data from {local_directory} uploaded to Drive folder '{drive_directory_name}' with ID: {drive_directory_id}"
    )


@click.command()
@click.argument("local_directory")
@click.argument("project_name")
def upload(local_directory, project_name):
    """Upload a local data directory to Google Drive."""
    click.echo(f"Uploading data to: {project_name}")
    subprocess.Popen(
        ["python", "mlcontrol.py", "upload_data", local_directory, project_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


mlcontrol.add_command(init)
mlcontrol.add_command(upload)

if __name__ == "__main__":
    mlcontrol()
