"""
Run this file to get robot and process data. You should only need to run this
file one time, when you make a new robot or when you make a new process. Save
the robot ID and the process release key to the .env file to be used in the
Discord bot's API calls. The ID and process release key should stay the same
and not need to be updated, unless the old robot or process cannot be used
for some reason.
"""
import os
import requests
from dotenv import load_dotenv

from PyJaC.uipath_functions import get_uipath_token

load_dotenv()

UIPATH_ACCOUNT_LOGICAL_NAME = os.getenv("UIPATH_ACCOUNT_LOGICAL_NAME")
UIPATH_USER_KEY = os.getenv("UIPATH_USER_KEY")
UIPATH_TENANT_NAME = os.getenv("UIPATH_TENANT_NAME")
UIPATH_CLIENT_ID = os.getenv("UIPATH_CLIENT_ID")
UIPATH_REFRESH_TOKEN = os.getenv("UIPATH_REFRESH_TOKEN")
UIPATH_PROCESS_KEY = os.getenv("UIPATH_PROCESS_KEY")
UIPATH_FID = os.getenv("UIPATH_FID")


def get_robots(access_token_given: str) -> str:
    """
    Makes a POST request to the UiPath API to retrieve the information of all
    the robots currently associated with a specified tenant. The ID of an
    unattended robot is required to run processes.

    :param access_token_given: A string representing the access token
    retrieved from the get_uipath_token() function. This is required to
    retrieve a user's information.
    :return: A string representing the data of all robots in JSON format. It is
    recommended to copy the string to format it to make it more readable.
    """
    url = "https://cloud.uipath.com/{}/{}/odata/Robots/" \
          "UiPath.Server.Configuration.OData.GetConfigured" \
          "Robots".format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-OrganizationUnitId": UIPATH_FID,
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "Authorization": "Bearer " + access_token_given
    }
    value = requests.get(url, headers=headers)
    return value.text


def get_process_keys(access_token_given):
    """
    Makes a POST request to the UiPath API to retrieve the information of all
    the processes currently associated with a specified tenant. The release
    key (denoted as "Key") of a process is required to be able to start it.

    :param access_token_given: A string representing the access token
    retrieved from the get_uipath_token() function. This is required to
    retrieve a user's information.
    :return: A string representing the data of all processes in JSON format.
    It is recommended to copy the string to format it to make it more readable.
    """
    url = "https://platform.uipath.com/{}/{}/odata/Releases" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "Authorization": "Bearer " + access_token_given
    }
    value = requests.get(url, headers=headers)
    return value.text


access_token = get_uipath_token()
print("============================ Process Keys ============================")
print(get_process_keys(access_token))
print("\n")
print("========================= Robots Information =========================")
print(get_robots(access_token))
