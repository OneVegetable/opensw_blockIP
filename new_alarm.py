import time
import re
import requests
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path, email, api_url):
        self.file_path = file_path #collect_ban_ip.txt
        self.email = email         
        self.api_url = api_url     #이메일 서버 url
        self.last_known_size = self.get_file_size()
        self.sent_ips = set() #이미 보낸 IP들을 추적하기 위한 집합
    #파일의 크기가 변하면 IP가 차단된 것으로 판단합니다.
    def get_file_size(self):
        try:
            print(os.path.getsize(self.file_path))
          
          
          
            return os.path.getsize(self.file_path)
        except FileNotFoundError:
            return 0

    def process_new_ips(self, file_path):
        with open(self.file_path, 'r', encoding = 'utf-8') as file:
            lines = file.readlines()
            if lines:
               
                return lines[-1]

    def extract_ip(self, log): 
        match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) - Blocked IP: (\d+\.\d+\.\d+\.\d+)", log)
        if match:
            date_time = match.group(1)
            ip_address = match.group(2)
            return date_time, ip_address
        else:
            return None, None

# 이메일 전송
    def send_email(self, message):	
        data = { 
            "email": self.email,
            "subject": "새롭게 차단된 IP",
            "message": message
        }
        response = requests.post(self.api_url, json=data) #서버 호출

        if response.status_code == 200:
            print(f"Email sent successfully to {self.email}")
        else:
            print(f"Failed to send email. Status code: {response.status_code}")

    def on_modified(self, event): #파일이 수정되면 실행되도록 합니다.
        
        log = self.process_new_ips(self.file_path)
        date_time, new_ip = self.extract_ip(log)
      
       # print(new_ip)
      

        if new_ip and new_ip not in self.sent_ips:
           
            message = f"비정상적인 IP의 접근이 감지되어,{date_time}에 해당 IP를 차단하였습니다.\n New banned IP(s) detected: {new_ip}"
            self.send_email(message)
            self.sent_ips.add(new_ip)

if __name__ == "__main__":
   
    
   
    current_dir = os.getcwd()
    file_name = "collect_ban_ip.txt"
    file_path = os.path.join(current_dir, file_name)
   
   # print(file_path)
    email = "" #사용자의 아이디를 적으면 됩니다. 예시) "abcde@fghi.com"
    api_url = "" #서버 아이피 주소와 포트 번호를 적으면 됩니다. 예시)  "http://000.000.000.000:0000/api/email/send?email={email}"

    event_handler = FileChangeHandler(file_path, email, api_url)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(file_path) or '.', recursive=False)
    
    print(f"Monitoring {file_path} for changes...")

    observer.start()
    try:
        while True:
            time.sleep(1) #1초마다 대상 디렉토리 감시
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
