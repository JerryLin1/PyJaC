from dotenv import load_dotenv
import requests
import os
import json

load_dotenv()

UIPATH_ACCOUNT_LOGICAL_NAME = os.getenv("UIPATH_ACCOUNT_LOGICAL_NAME")
UIPATH_USER_KEY = os.getenv("UIPATH_USER_KEY")
UIPATH_TENANT_NAME = os.getenv("UIPATH_TENANT_NAME")
UIPATH_CLIENT_ID = os.getenv("UIPATH_CLIENT_ID")
UIPATH_REFRESH_TOKEN = os.getenv("UIPATH_REFRESH_TOKEN")
UIPATH_PROCESS_KEY = os.getenv("UIPATH_PROCESS_KEY")
UIPATH_FID = os.getenv("UIPATH_FID")
UIPATH_ROBOT_ID = os.getenv("UIPATH_ROBOT_ID")


# Returns the the UiPath access token which is needed to make calls to the
# UiPath Orchestrator API. Expires every 24 hours
# Requires .env file to be configured with UiPath account tenant info
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


def start_job(access_token):
    url = " https://cloud.uipath.com/{}/{" \
          "}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "X-UIPATH-OrganizationUnitId": UIPATH_FID,
        "Authorization": "Bearer " + access_token
    }
    input_arguments = {
        "text": "SUP!"
    }
    data = {
        "startInfo": {
            "ReleaseKey": UIPATH_PROCESS_KEY,
            "RobotIds": [int(UIPATH_ROBOT_ID)],
            "JobsCount": 0,
            "Strategy": "Specific",
            # "InputArguments": input_arguments,
        }
    }
    data = str(data).replace("'", '"')
    print(data)

    value = requests.post(url, data=data, headers=headers)
    print(value.text)


r = "5af0a4ba-32e0-41ed-84ee-31196da47e72"
access_token = get_uipath_token()
start_job(access_token)
