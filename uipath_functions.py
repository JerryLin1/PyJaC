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


def get_uipath_token() -> str:
    """
    Calls a POST request to the UiPath API to retrieve the access token
    linked with the specified tenant. The access token is then required for
    every subsequent call to the UiPath API.

    :return: A string representing the access token.
    """
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

    data = str(data).replace("'", '"')

    value = requests.post(url, headers=headers, data=data)

    auth_json = json.loads(value.text)
    return auth_json['access_token']


def start_job(access_token: str, input_arguments: dict) -> dict:
    """
    Calls a POST request to the UiPath Orchestrator API using environment
    variables to start the process, which will then call the OpenWeatherMap
    API using the input arguments. It will then return the weather data from
    OpenWeatherMap.

    :param access_token: The access token retrieved from get_uipath_token().
    :param input_arguments: A dictionary in JSON format that represents the
    input arguments that are passed to the UiPath process. The UiPath process
    has 3 possible input arguments: "location", which represents the city
    that the weather data is to be pulled from. It is denoted by "[CITY],
    [COUNTRY CODE]" in which the country code is optional. "discordName"
    represents the Discord username of the user who requests the data.
    "units" represents the unit system of the weather data that is to be
    returned. Possible values are "standard", "imperial", and "metric".
    :return: A dictionary in JSON format that represents the output arguments
    of the UiPath process.
    """
    url = "https://cloud.uipath.com/{}/{}/" \
          "odata/Jobs/UiPath.Server.Configuration.OData.StartJobs" \
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

    url2 = "https://platform.uipath.com/{}/{}/odata/Jobs?$filter=Id eq {}" \
        .format(UIPATH_ACCOUNT_LOGICAL_NAME, UIPATH_TENANT_NAME, job_id)
    # Continuously check for completion of the process using its id
    job_status = requests.get(url2, headers=headers).json()["value"][0]
    while job_status["State"] != "Successful":
        time.sleep(0.2)
        job_status = requests.get(url2, headers=headers).json()["value"][0]
    # Return the output arguments of the process once it's complete
    return json.loads(json.loads(job_status["OutputArguments"])["results"])
