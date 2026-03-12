import requests
from requests.auth import HTTPDigestAuth

CAMERA_IP = "192.168.1.64"          
USERNAME = "admin"                  
OLD_PASSWORD = "password123"    
NEW_PASSWORD = "password456"    

url = f"http://{CAMERA_IP}/ISAPI/Security/users/1"

xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<User version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
  <id>1</id>
  <userName>{USERNAME}</userName>
  <password>{NEW_PASSWORD}</password>
</User>
"""

headers = {"Content-Type": "application/xml"}

resp = requests.put(
    url,
    auth=HTTPDigestAuth(USERNAME, OLD_PASSWORD),
    data=xml_payload.encode("utf-8"),
    headers=headers,
    timeout=10
)

print("Status:", resp.status_code)
print(resp.text)