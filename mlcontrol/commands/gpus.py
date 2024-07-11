import click
import subprocess


@click.command()
@click.argument("filters")
@click.option("--help", "help", flag_value=True)
def gpus(help, filters) -> None:
    """Lists available GPUs provided by Vast.ai cloud service."""
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
    command = f"vastai search offers '{filters}'"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()
