import click
import subprocess


@click.command()
@click.option("--gpu_ram", type=float, help="Per GPU RAM in GB")
@click.option(
    "--gpu_arch", type=str, help="Host machine GPU architecture (e.g., nvidia, amd)"
)
@click.option("--disk_space", type=float, help="Disk storage space in GB")
@click.option("--help", "help_flag", is_flag=True, help="Show help information")
def gpus(gpu_ram, gpu_arch, disk_space, help_flag) -> None:
    """Lists available GPUs provided by Vast.ai cloud service."""

    if help_flag:
        click.echo(
            """
Available Filters:
  disk_space: float       Disk storage space, in GB
  gpu_arch: string        Host machine GPU architecture (e.g., nvidia, amd)
  gpu_ram: float          Per GPU RAM in GB
            """
        )
        return

    filters = []

    if gpu_ram:
        filters.append(f"gpu_ram>={gpu_ram}")
    if gpu_arch:
        filters.append(f"gpu_arch={gpu_arch}")
    if disk_space:
        filters.append(f"disk_space>={disk_space}")

    filters.append("rentable=True")
    filters.append("verified=True")

    filter_string = " ".join(filters)

    command = f"vastai search offers '{filter_string}'"
    click.echo(f"Running command: {command}")

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()


if __name__ == "__main__":
    gpus()
