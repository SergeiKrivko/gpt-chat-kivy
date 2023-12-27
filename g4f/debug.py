from os import environ
from requests import get
from importlib.metadata import version as get_package_version, PackageNotFoundError
# from subprocess import check_output, CalledProcessError, PIPE
from .errors import VersionNotFoundError

logging = False
version_check = False
    
def get_latest_version() -> str:
    response = get("https://pypi.org/pypi/g4f/json").json()
    return response["info"]["version"]

def check_pypi_version() -> None:
    pass
