import click
from mlcontrol.utils import Services
import googleapiclient

SERVICES = Services()


@click.command()
def list_projects() -> None:
    """Lists all top-level project folders on Google Drive."""
    click.echo("Listing all top-level project folders...")

    service = SERVICES.authenticate()

    try:
        response = (
            service.files()
            .list(
                q="mimeType='application/vnd.google-apps.folder' and 'root' in parents",
                spaces="drive",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )

        projects = response.get("files", [])

        if not projects:
            click.echo("No top-level projects found.")
        else:
            click.echo("Top-level project folders:")
            for project in projects:
                click.echo(f"- {project['name']} (ID: {project['id']})")

    except googleapiclient.errors.HttpError as e:
        click.echo(f"Google Drive API Error: {e}")
        return


if __name__ == "__main__":
    list_projects()
