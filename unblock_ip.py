import os
import argparse
from datetime import datetime
from pathlib import Path

   
current_dir = os.getcwd()
file_name = "unblock_ip.txt"
UNBLOCKED_IP_FILE = os.path.join(current_dir, file_name)

def unblock_ip(ip):
    unblocked_ip_path = Path(UNBLOCKED_IP_FILE)
    if not unblocked_ip_path.exists():
        unblocked_ip_path.touch()

    with unblocked_ip_path.open('a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Unblocked IP: {ip}\n")

    os.system(f'sudo iptables -D INPUT -s {ip} -j DROP')
    print(f"IP {ip} has been unblocked.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Unblock an IP address.')
    parser.add_argument('ip', type=str, help='The IP address to unblock')

    args = parser.parse_args()
    ip_to_unblock = args.ip

    unblock_ip(ip_to_unblock)

