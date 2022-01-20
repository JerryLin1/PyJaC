import time

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


def start_job(access_token, input_arguments):
    url = "https://cloud.uipath.com/{}/{" \
          "}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME)
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": UIPATH_TENANT_NAME,
        "X-UIPATH-OrganizationUnitId": UIPATH_FID,
        "Authorization": "Bearer " + access_token
    }

    data = {
        "startInfo": {
            "ReleaseKey": UIPATH_PROCESS_KEY,
            "RobotIds": [int(UIPATH_ROBOT_ID)],
            "Strategy": "Specific",
            "InputArguments": json.dumps(input_arguments),
        }
    }

    data = json.dumps(data)
    # print(data)

    # This post request starts the process
    job_info = requests.post(url, data=data, headers=headers).json()["value"][0]
    # Store the id to be used in next part
    job_id = job_info["Id"]

    url2 = "https://platform.uipath.com/{}/{" \
           "}/odata/Jobs?$filter=Id eq {}" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME, job_id)
    # Continuously check for completion of the process using its id
    job_status = requests.get(url2, headers=headers).json()["value"][0]
    while job_status["State"] != "Successful":
        time.sleep(0.2)
        job_status = requests.get(url2, headers=headers).json()["value"][0]
    # Return the output arguments of the process once it's complete
    return json.loads(json.loads(job_status["OutputArguments"])["results"])


access_token = get_uipath_token()
input_arguments = {
    "location": "London,CA"
}
output = start_job(access_token, input_arguments)
print(output)
