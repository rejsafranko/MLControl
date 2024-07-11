import os
import sys
import click
import googleapiclient
import googleapiclient.http
from mlcontrol.utils import Services

SERVICES = Services()


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
                media = googleapiclient.http.MediaFileUpload(file_path, resumable=True)
                service.files().create(
                    body=file_metadata, media_body=media, fields="id"
                ).execute()
                sys.stdout.flush()  # Ensure the progress bar updates

        click.echo(
            f"Data from {local_directory} uploaded to Drive folder '{project_name}'."
        )

    except Exception as e:
        click.echo(f"Error uploading data: {e}")
