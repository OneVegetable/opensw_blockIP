import re
from collections import deque
from datetime import datetime
import pytz

def parse_auth_log(logfile_path='/var/log/auth.log', output_file='failed_logins.txt', num_records=15, log_tz='UTC', local_tz='Asia/Seoul'):
    # 로그인 실패를 나타내는 패턴 정의
    failed_login_patterns = [
        re.compile(r"Invalid user (\S+) from (\S+) port \d+"),  # (Invalid user) 로그 패턴, IP 주소 포함
        re.compile(r"Connection closed by invalid user (\S+) from (\S+) port \d+"),  # (Connection closed by invalid user) 로그 패턴, IP 주소 포함
    ]

    # 최근 기록을 저장할 deque, 최대 저장 수: num_recoreds
    recent_records = deque(maxlen=num_records)
    log_timezone = pytz.timezone(log_tz) # 로그 파일에 기록된 시간대
    local_timezone = pytz.timezone(local_tz) # 변환할 로컬 시간대

    try:
        with open(logfile_path, 'r') as file:
            for line in file:
                # 패턴을 사용하여 로그인 실패를 검사
                for pattern in failed_login_patterns:
                    match = pattern.search(line)
                    if match:
                        date_time_str = ' '.join(line.split()[:3])  # 로그에서 날짜와 시간 추출
                        date_time_obj = datetime.strptime(date_time_str, '%b %d %H:%M:%S')  # 날짜와 시간을 datetime 객체로 변환
                        date_time_obj = date_time_obj.replace(year=datetime.now().year)  # 연도 추가


                        # 로그 시간대를 적용하고 로컬 시간대로 변환
                        log_time = log_timezone.localize(date_time_obj)
                        local_time = log_time.astimezone(local_timezone)

                        username = match.group(1)
                        ip_address = match.group(2)
                        recent_records.append(f"날짜: {local_time.strftime('%Y-%m-%d %H:%M:%S')}, 사용자 이름: {username}, IP 주소: {ip_address}")

    except FileNotFoundError:
        # 로그 파일이 없을 때 예외 처리
        print(f"Error: The file {logfile_path} does not exist.")
        return
    except PermissionError:
        # 로그 파일 읽기 권한이 없을 때 예외 처리
        print(f"Error: Permission denied to read the file {logfile_path}.")
        return

    # 최근 기록을 파일에 저장하고 동시에 출력
    try:
        with open(output_file, 'w') as file:
            if recent_records:
                print(f"실패한 로그인 시도 최근 {num_records}개")
                file.write(f"실패한 로그인 시도 최근 {num_records}개\n")
                for record in recent_records:
                    print(record)
                    file.write(record + '\n')
            else:
                print("No failed login attempts found.")
                file.write("No failed login attempts found.\n")

    except IOError as e:
        print(f"Error: Unable to write to file {output_file}. {e}")

if __name__ == "__main__":
    parse_auth_log()
