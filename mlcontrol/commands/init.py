import click
from mlcontrol.utils import Services

SERVICES = Services()

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
