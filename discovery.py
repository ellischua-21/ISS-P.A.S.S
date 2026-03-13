import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    if local_ip.startswith("127."):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            local_ip = sock.getsockname()[0]
        finally:
            sock.close()

    return local_ip


def get_local_subnet_hosts():
    local_ip = get_local_ip()
    ip_parts = local_ip.split(".")
    subnet_base = ".".join(ip_parts[:3])

    return [
        f"{subnet_base}.{i}"
        for i in range(1, 255)
        if f"{subnet_base}.{i}" != local_ip
    ]


def is_hikvision_device(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.8)

    try:
        result = sock.connect_ex((ip, 80))
        if result != 0:
            return False
    finally:
        sock.close()

    try:
        response = requests.get(
            f"http://{ip}/ISAPI/System/deviceInfo",
            timeout=1.5,
            allow_redirects=False
        )

        auth_header = response.headers.get("WWW-Authenticate", "").lower()

        if response.status_code == 200 and "DeviceInfo" in response.text:
            return True

        if response.status_code == 401 and "digest" in auth_header:
            return True

    except requests.RequestException:
        pass

    return False


def discover_devices():
    hosts = get_local_subnet_hosts()
    found_devices = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_map = {
            executor.submit(is_hikvision_device, ip): ip
            for ip in hosts
        }

        for future in as_completed(future_map):
            ip = future_map[future]

            try:
                if future.result():
                    found_devices.append(ip)
            except Exception:
                pass

    return sorted(found_devices, key=lambda x: tuple(map(int, x.split("."))))