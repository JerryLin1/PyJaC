from dotenv import load_dotenv
import requests
import os
import json


# Returns the the UiPath access token which is needed to make calls to the
# UiPath Orchestrator API. Expires every 24 hours
# Requires .env file to be configured with UiPath account tenant info
def get_uipath_token():
    load_dotenv()

    tenant_name = os.getenv("UIPATH_TENANT_NAME")
    client_id = os.getenv("UIPATH_CLIENT_ID")
    refresh_token = os.getenv("UIPATH_REFRESH_TOKEN")

    url = "https://account.uipath.com/oauth/token"
    headers = {
        "Content-Type": "application/json",
        "X-UIPATH-TenantName": tenant_name
    }

    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token
    }

    # For some reason only " works and not ' when making API call
    data = str(data).replace("'", '"')

    value = requests.post(url, headers=headers, data=data)

    auth_json = json.loads(value.text)
    access_token = auth_json['access_token']
    return access_token


print("Access Token is: "+get_uipath_token())
