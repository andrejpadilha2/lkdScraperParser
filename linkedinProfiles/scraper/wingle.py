from time import sleep
import requests
import socket
import huaweisms.api.user
import huaweisms.api.wlan
import huaweisms.api.dialup
import huaweisms.api.device

def rotate_ip():
    ip = get_ip_address()
    print("→ Current IP Address:", ip)
    
    ctx = huaweisms.api.user.quick_login("admin", "admin")
    print("→ Rebooting wingle")
    huaweisms.api.device.reboot(ctx)
    sleep(20)
    while not check_internet_connection():
        sleep(5)
        pass
    ctx = huaweisms.api.user.quick_login("admin", "admin")
    mobile_status = huaweisms.api.dialup.get_mobile_status(ctx)
    print(f"→ Mobile status: {mobile_status}")
    
    ip = get_ip_address()
    print("→ New IP Address:", ip)

def get_ip_address():
    url = 'https://api.ipify.org'
    while True:
        try:
            response = requests.get(url)
            break
        except Exception as e:
            # print(e)
            print("→ Trying to get new IP Address.")
    ip_address = response.text
    return ip_address

def check_internet_connection():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("google.com", 80))
        sock.close()
        return True
    except socket.error as e:
        print("→ Still not connected to the internet, waiting 5 more seconds.")
        return False