import sys
import click
from mlcontrol.commands import init, upload, list, gpus, list_projects


@click.group()
def mlcontrol():
    pass


mlcontrol.add_command(init)
mlcontrol.add_command(upload)
mlcontrol.add_command(list)
mlcontrol.add_command(list_projects)
mlcontrol.add_command(gpus)


def print_banner():
    print(
        """
    __  _____    ______            __             __
   /  |/  / /   / ____/___  ____  / /__________  / /
  / /|_/ / /   / /   / __ \/ __ \/ __/ ___/ __ \/ / 
 / /  / / /___/ /___/ /_/ / / / / /_/ /  / /_/ / /  
/_/  /_/_____/\____/\____/_/ /_/\__/_/   \____/_/   
                                                   
CLI tool for MLOps tasks. 
        """
    )


def main():
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "mlcontrol"):
        print_banner()
    mlcontrol()


if __name__ == "__main__":
    main()
