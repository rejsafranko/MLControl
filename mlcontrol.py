import os
import click
import subprocess
import google.auth
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Define scopes.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def authenticate() -> googleapiclient.discovery.Resource:
    """
    Authenticate the user and return a Google Drive service object.

    This function handles authentication for accessing Google Drive API using OAuth 2.0.
    It checks for existing credentials in 'token.json' file. If credentials are not found
    or are invalid/expired, it initiates the OAuth flow to obtain new credentials and saves
    them to 'token.json' for future use.

    Returns:
        googleapiclient.discovery.Resource: A resource object for interacting with Google Drive API.

    Raises:
        FileNotFoundError: If 'credentials.json' file is not found in the current directory.
        google.auth.exceptions.RefreshError: If credentials cannot be refreshed.
        google.auth.exceptions.OAuthError: If there's an OAuth authentication error.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = google.auth.load_credentials_from_file("token.json", SCOPES)[0]

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build and return the Google Drive service object
    return googleapiclient.discovery.build("drive", "v3", credentials=creds)


from googleapiclient.discovery import Resource


def create_directory(service: Resource, name: str, parent_id: int = None) -> int:
    """
    Create a directory on Google Drive.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Drive service object.
        name (str): The name of the directory to create.
        parent_id (int, optional): The ID of the parent directory where the new directory will be created.
                                   Defaults to None if creating at the root level.

    Returns:
        int: The ID of the newly created directory on Google Drive.

    Raises:
        googleapiclient.errors.HttpError: If an error occurs while attempting to create the directory.
    """
    file_metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        file_metadata["parents"] = [parent_id]

    try:
        file: dict[str, int] = (
            service.files().create(body=file_metadata, fields="id").execute()
        )
        return file.get("id")
    except googleapiclient.errors.HttpError as e:
        raise googleapiclient.errors.HttpError(
            f"An error occurred while creating directory '{name}' on Google Drive: {e}"
        )


@click.group()
def cli():
    pass


@click.command()
@click.argument("project_name")
def create_project(project_name: str) -> None:
    """
    Create a project directory template on Google Drive.

    Args:
        project_name (str): The name of the project directory to create on Google Drive.

    Returns:
        None

    Raises:
        googleapiclient.errors.HttpError: If an error occurs while interacting with the Google Drive API.
    """
    service = authenticate()

    # Create main project directory
    project_id = create_directory(service, project_name)

    # Create subdirectories
    create_directory(service, "data", project_id)
    create_directory(service, "models", project_id)

    click.echo(f"Project {project_name} created with ID: {project_id}")


def find_folder_by_name(service, folder_name, parent_id=None):
    """
    Find a folder on Google Drive by name.

    Args:
        service (googleapiclient.discovery.Resource): An authenticated Google Drive service object.
        folder_name (str): The name of the folder to find.
        parent_id (str, optional): The ID of the parent directory where the folder will be searched.
                                   Defaults to None for searching in the root.

    Returns:
        str: The ID of the found folder.

    Raises:
        ValueError: If no folder with the specified name is found.
        HttpError: If an error occurs while interacting with the Google Drive API.
    """
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    try:
        response = (
            service.files().list(q=query, spaces="drive", fields="files(id)").execute()
        )
        folders = response.get("files", [])

        if not folders:
            raise ValueError(f"No folder named '{folder_name}' found in Google Drive.")

        if len(folders) > 1:
            raise ValueError(
                f"Multiple folders named '{folder_name}' found in Google Drive."
            )

        return folders[0]["id"]

    except googleapiclient.errors.HttpError as e:
        raise googleapiclient.errors.HttpError(
            f"An error occurred while searching for folder '{folder_name}' on Google Drive: {e}"
        )


@click.command()
@click.argument("local_directory")
@click.argument("drive_directory_name")
def upload_data(local_directory, drive_directory_name):
    """
    Upload a local data directory to Google Drive.

    Args:
        local_directory (str): Path to the local data directory to upload.
        drive_directory_name (str): Name of the Google Drive directory where data will be uploaded.

    Returns:
        None
    """
    service = authenticate()

    try:
        drive_directory_id = find_folder_by_name(service, drive_directory_name)
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
@click.argument("project_name")
def init(project_name):
    """Initialize a new MLOps project on Google Drive."""
    click.echo(f"Initializing new MLOps project: {project_name}")
    subprocess.Popen(
        ["python", "mlcontrol.py", "create_project", project_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


@click.command()
@click.argument("local_directory")
@click.argument("drive_directory_id")
def upload(local_directory, drive_directory_id):
    """Upload data to an existing MLOps project on Google Drive."""
    click.echo(
        f"Uploading data from {local_directory} to Drive folder ID: {drive_directory_id}"
    )
    subprocess.Popen(
        ["python", "mlcontrol.py", "upload_data", local_directory, drive_directory_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


cli.add_command(create_project)
cli.add_command(upload_data)
cli.add_command(init)
cli.add_command(upload)

if __name__ == "__main__":
    cli()
