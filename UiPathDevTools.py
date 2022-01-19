import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

UIPATH_ACCOUNT_LOGICAL_NAME = os.getenv("UIPATH_ACCOUNT_LOGICAL_NAME")
UIPATH_USER_KEY = os.getenv("UIPATH_USER_KEY")
UIPATH_TENANT_NAME = os.getenv("UIPATH_TENANT_NAME")
UIPATH_CLIENT_ID = os.getenv("UIPATH_CLIENT_ID")
UIPATH_REFRESH_TOKEN = os.getenv("UIPATH_REFRESH_TOKEN")
UIPATH_PROCESS_KEY = os.getenv("UIPATH_PROCESS_KEY")
UIPATH_FID = os.getenv("UIPATH_FID")


# For dev use only

def get_uipath_token():
    url = "https://account.uipath.com/oauth/token"
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME
    }

    data = {
        "grant_type": "refresh_token",
        "client_id": UIPATH_CLIENT_ID,
        "refresh_token": UIPATH_REFRESH_TOKEN
    }

    # For some reason only " works and not ' when making API call
    data = str(data).replace("'", '"')

    value = requests.post(url, headers=headers, data=data)

    auth_json = json.loads(value.text)
    return auth_json['access_token']


# Run to get all information of robots. You will need the id of an unattended
# robot to be able to run processes
def get_robots(access_token):
    url = "https://cloud.uipath.com/{}/{" \
          "}/odata/Robots/UiPath.Server.Configuration.OData" \
          ".GetConfiguredRobots" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-OrganizationUnitId": UIPATH_FID,
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "Authorization": "Bearer " + access_token
    }
    value = requests.get(url, headers=headers)
    print(value.text)


# Run to get all information of a user's processes. You will need the release
# key, known just as "Key" associated with a process to be able to run it
def get_process_keys(access_token):
    url = "https://platform.uipath.com/{}/{}/odata/Releases" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "Authorization": "Bearer " + access_token
    }
    value = requests.get(url, headers=headers)
    print(value.text)


access_token = get_uipath_token()
print(
    "============================= Process Keys =============================")
get_process_keys(access_token)
print("\n")
print(
    "========================== Robots Information ==========================")
get_robots(access_token)
