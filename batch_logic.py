import re
import time
import requests
from requests.auth import HTTPDigestAuth


def is_valid_password(password: str):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, "Password is valid."


def change_camera_password(ip: str, username: str, current_password: str, new_password: str, timeout: int = 10):
    url = f"http://{ip}/ISAPI/Security/users/1"

    xml_payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<User version="2.0" xmlns="http://www.hikvision.com/ver20/XMLSchema">
    <id>1</id>
    <userName>{username}</userName>
    <password>{new_password}</password>
</User>
"""

    headers = {
        "Content-Type": "application/xml"
    }

    try:
        response = requests.put(
            url,
            auth=HTTPDigestAuth(username, current_password),
            data=xml_payload.encode("utf-8"),
            headers=headers,
            timeout=timeout
        )

        if response.status_code in (200, 204):
            return True, f"{ip} -> Password changed successfully."
        elif response.status_code == 401:
            return False, f"{ip} -> Incorrect username or password."
        elif response.status_code == 403:
            return False, f"{ip} -> Password does not meet policy."
        else:
            return False, f"{ip} -> Failed ({response.status_code})"

    except requests.exceptions.ConnectTimeout:
        return False, f"{ip} -> Connection timed out."
    except requests.exceptions.ConnectionError:
        return False, f"{ip} -> Device unreachable."
    except Exception as e:
        return False, f"{ip} -> Error: {str(e)}"


def batch_change_password(ip_list, username, current_password, new_password, retries=1, delay_between_devices=1):

    results = []

    for ip in ip_list:

        success = False
        message = ""

        for attempt in range(retries + 1):

            ok, result_message = change_camera_password(
                ip,
                username,
                current_password,
                new_password
            )

            message = result_message

            if ok:
                success = True
                break

            if attempt < retries:
                time.sleep(1)

        results.append({
            "ip": ip,
            "success": success,
            "message": message
        })

        time.sleep(delay_between_devices)

    return results