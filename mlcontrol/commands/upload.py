import os
import sys
import click
import googleapiclient
import googleapiclient.http
from mlcontrol.utils import Services, Spinner
import threading
import time

SERVICES = Services()


@click.command()
@click.option(
    "-d", "--data", "upload_type", flag_value="data", default=True, help="Upload data"
)
@click.option("-m", "--model", "upload_type", flag_value="model", help="Upload model")
@click.argument("local_directory")
@click.argument("project_name")
def upload(upload_type, local_directory: str, project_name: str) -> None:
    """Upload a local data or model directory to Google Drive."""
    if upload_type == "data":
        click.echo(f"Uploading data to: {project_name}")
    else:
        click.echo(f"Uploading model to: {project_name}")

    sys.stdout.flush()
    service = SERVICES.authenticate()

    try:
        project_id = SERVICES.find_folder_by_name(service, project_name)
        folder_name = "data" if upload_type == "data" else "models"
        target_folder_id = SERVICES.find_folder_by_name(
            service, folder_name, parent_id=project_id
        )
        folder_name_for_upload = SERVICES.parse_dataset_name(local_directory)
        upload_folder_id = SERVICES.create_directory(
            service, folder_name_for_upload, target_folder_id
        )
    except ValueError as e:
        click.echo(f"Error: {e}")
        return
    except googleapiclient.errors.HttpError as e:
        click.echo(f"Google Drive API Error: {e}")
        return

    spinner = Spinner()
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(target=spinner.spinner, args=(stop_spinner,))
    spinner_thread.start()
    time.sleep(2)

    try:
        for root, dirs, files in os.walk(local_directory):
            files_list = list(files)
            for filename in SERVICES.custom_progress_bar(
                files_list, prefix=f"Uploading {upload_type}: ", size=len(files_list)
            ):
                file_path = os.path.join(root, filename)
                file_metadata = {"name": filename, "parents": [upload_folder_id]}
                media = googleapiclient.http.MediaFileUpload(file_path, resumable=True)
                service.files().create(
                    body=file_metadata, media_body=media, fields="id"
                ).execute()
                sys.stdout.flush()

        stop_spinner.set()
        spinner_thread.join()

        click.echo(
            f"{upload_type.capitalize()} from {local_directory} uploaded to Drive folder '{project_name}'."
        )

    except Exception as e:
        stop_spinner.set()
        spinner_thread.join()
        click.echo(f"Error uploading {upload_type}: {e}")


if __name__ == "__main__":
    upload()
