import requests
from requests.auth import HTTPDigestAuth

CAMERA_IP = "192.168.1.64"
USERNAME = "admin"
PASSWORD = "newpassword123"

url = f"http://{CAMERA_IP}/ISAPI/Security/users"
resp = requests.get(url, auth=HTTPDigestAuth(USERNAME, PASSWORD), timeout=10)

print("Status:", resp.status_code)
print(resp.text)