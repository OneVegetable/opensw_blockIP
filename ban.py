import re
import os
import pytz
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
import subprocess

# 설정
current_dir = os.getcwd()
file_name = "failed_logins.txt"

LOG_FILE_PATH = os.path.join(current_dir, file_name)
BLOCKED_IP_FILE = 'collect_ban_ip.txt'
KST = pytz.timezone('Asia/Seoul')

# IP 접근 기록 저장 딕셔너리
access_records = defaultdict(list)

def parse_log_line(line):
    match = re.match(r"날짜: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), 사용자 이름: \S+, IP 주소: (\d+\.\d+\.\d+\.\d+)", line)
    if match:
        date_time_str, ip = match.groups()
        timestamp = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        timestamp = KST.localize(timestamp)
        return timestamp, ip
    return None

def block_ip(ip):
    """
    IP를 차단하고 차단 정보를 파일에 기록
    """
    try:
        result = subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'], check=True)
        print("IP 차단 성공")

        # 차단된 IP를 파일에 기록
        record_blocked_ip(ip)

    except subprocess.CalledProcessError as e:
        print("IP 차단 실패:", e)


def record_blocked_ip(ip):
    """
    차단된 IP를 BLOCKED_IP_FILE에 기록합니다.
    """
    now = datetime.now(KST)  # 현재 시간을 KST로 설정
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    log_entry = f"{timestamp} - Blocked IP: {ip}\n"
    
    try:
        with open(BLOCKED_IP_FILE, 'a') as file:
            file.write(log_entry)
        print(f"IP 기록 성공: {ip}")
    except IOError as e:
        print(f"IP 기록 실패: {ip} - {e}")


def process_logs():
    """
    로그 파일에서 최근 30개의 로그 항목을 읽고 처리합니다.
    """
    log_file = Path(LOG_FILE_PATH)
    if not log_file.exists():
        print(f"Error: Log file {LOG_FILE_PATH} does not exist.")
        return

    
    with open(LOG_FILE_PATH, 'r', encoding='UTF8') as f: 
        lines = f.readlines()
        if len(lines) == 0:
            print("Log file is empty.")
            return

        recent_lines = lines[-30:]  # 최근 30개 로그 줄 가져오기 ( 변동가능 )

    now = datetime.now(KST)
    ip_to_check = set()

    # 로그 처리
    for line in recent_lines:
        parsed = parse_log_line(line)
        if parsed:
            timestamp, ip = parsed
            print(f"Parsed Log - Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}, IP: {ip}")

            if ip != 'N/A':
                access_records[ip].append(timestamp)
                ip_to_check.add(ip)


    # 각 IP별 최근 1초 이내의 시도 횟수 확인
    for ip in ip_to_check:
        recent_attempts = [t for t in access_records[ip] if now - t <= timedelta(seconds=1)]
        if len(recent_attempts) > 5: # 1초당 차단하고싶은 접근 횟수를 적어주세요.
            print(f"Blocking IP: {ip}")
            block_ip(ip)
            access_records[ip] = []



if __name__ == "__main__":
    process_logs()
