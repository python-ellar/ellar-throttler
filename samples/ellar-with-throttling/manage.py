import os

from ellar.common.constants import ELLAR_CONFIG_MODULE
from ellar_cli.main import create_ellar_cli

if __name__ == "__main__":
    os.environ.setdefault(ELLAR_CONFIG_MODULE, "throttling_sample.config:DevelopmentConfig")

    # initialize Commandline program
    cli = create_ellar_cli("throttling_sample.server:app")
    # start commandline execution
    cli(prog_name="Ellar Web Framework CLI")
