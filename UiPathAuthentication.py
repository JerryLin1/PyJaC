from dotenv import load_dotenv
import requests
import os
import json

load_dotenv()

TENANT_NAME = os.getenv("TENANT_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

url = "https://account.uipath.com/oauth/token"
headers = {
    "Content-Type": "application/json",
    "X-UIPATH-TenantName": TENANT_NAME
}

data = {
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
    "refresh_token": REFRESH_TOKEN
}

# For some reason only " works and not ' when making API call
data = str(data).replace("'", '"')

returnValue = requests.post(url, headers=headers, data=data)

authJson = json.loads(returnValue.text)
print(authJson)
access_token = authJson['access_token']
