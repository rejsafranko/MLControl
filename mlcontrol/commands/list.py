import click
import googleapiclient.errors
from mlcontrol.utils import Services, SubdirectoryNotFoundError

SERVICES = Services()


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
