import requests
from requests.auth import HTTPDigestAuth

CAMERA_IP = "192.168.90.104"

SERVICE_USERNAME = "service"
SERVICE_PASSWORD = "password123"

NEW_SERVICE_PASSWORD = "password456"
NEW_USER_PASSWORD = "password456"
NEW_LIVE_PASSWORD = "password456"

url = f"http://{CAMERA_IP}/rcp.xml"

payload = {
    "command": "userManagement.setPassword",
    "user": "service",
    "password": NEW_SERVICE_PASSWORD
}

try:
    response = requests.post(
        url,
        auth=HTTPDigestAuth(SERVICE_USERNAME, SERVICE_PASSWORD),
        data=payload,
        timeout=10
    )

    print("Status:", response.status_code)
    print("Response:")
    print(response.text)

except Exception as e:
    print("Error:", e)