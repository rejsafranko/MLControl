import os
import sys
import click
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
import google_auth_oauthlib.flow


class Services:
    def __init__(self):
        self.google_api_scopes = ["https://www.googleapis.com/auth/drive.file"]

    def authenticate(self) -> googleapiclient.discovery.Resource:
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
        credentials = None
        if os.path.exists("token.json"):
            credentials = (
                google.oauth2.credentials.Credentials.from_authorized_user_file(
                    "token.json", self.google_api_scopes
                )
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(google.auth.transport.requests.Request())
            else:
                flow = (
                    google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                        "credentials.json", self.google_api_scopes
                    )
                )
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run.
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

        return googleapiclient.discovery.build("drive", "v3", credentials=credentials)

    def create_directory(
        self,
        service: googleapiclient.discovery.Resource,
        name: str,
        parent_id: int = None,
    ) -> int:
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

    def find_folder_by_name(
        self,
        service: googleapiclient.discovery.Resource,
        folder_name: str,
        parent_id: int = None,
    ) -> str:
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
        query = (
            f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
        )
        if parent_id:
            query += f" and '{parent_id}' in parents"

        try:
            response = (
                service.files()
                .list(q=query, spaces="drive", fields="files(id)")
                .execute()
            )
            folders = response.get("files", [])

            if not folders:
                raise ValueError(
                    f"No folder named '{folder_name}' found in Google Drive."
                )

            if len(folders) > 1:
                raise ValueError(
                    f"Multiple folders named '{folder_name}' found in Google Drive."
                )

            return folders[0]["id"]

        except googleapiclient.errors.HttpError as e:
            raise googleapiclient.errors.HttpError(
                f"An error occurred while searching for folder '{folder_name}' on Google Drive: {e}"
            )

    def list_folders(
        self, service: googleapiclient.discovery.Resource, parent_id: str
    ) -> list[dict]:
        """
        List all folders within a specified parent folder on Google Drive.

        Args:
            service (googleapiclient.discovery.Resource): An authenticated Google Drive service object.
            parent_id (str): The ID of the parent folder.

        Returns:
            list[dict]: A list of dictionaries, each representing a subfolder with its 'name' and 'id'.

        Raises:
            googleapiclient.errors.HttpError: If an error occurs while interacting with the Google Drive API.
        """
        query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'"
        try:
            response = (
                service.files()
                .list(q=query, spaces="drive", fields="files(id, name)")
                .execute()
            )
            folders = response.get("files", [])
            return folders
        except googleapiclient.errors.HttpError as e:
            raise googleapiclient.errors.HttpError(
                f"An error occurred while listing folders in parent '{parent_id}' on Google Drive: {e}"
            )

    def parse_dataset_name(self, path: str) -> str:
        # Remove trailing slash if present
        if path.endswith("/"):
            path = path[:-1]

        # Split path by '/' and return the last element
        dataset_name = path.split("/")[-1]

        return dataset_name

    def custom_progress_bar(self, iterable, prefix="", size=60, file=sys.stdout):
        count = len(iterable)

        def show(j):
            x = int(size * j / count)
            click.echo(
                f"{prefix}[{'#' * x}{'.' * (size - x)}] {j}/{count}",
                file=file,
                nl=False,
            )
            file.flush()

        show(0)
        for i, item in enumerate(iterable):
            yield item
            show(i + 1)
        click.echo("", file=file)
