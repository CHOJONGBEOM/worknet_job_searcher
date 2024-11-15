from time import sleep
from worknet_browser import browser
from worknet_crawling import crawling
from playwright.sync_api import sync_playwright
import csv
import datetime
import re


url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?staArea=&programMenuIdentification=EBG020000000002&indArea="
search = "데이터 분석가 마케팅"
page, context = browser(url, search)
jobs_db = crawling(page, context)

safe_search = re.sub(r'[\\/*?:"<>|]', "", search)  # 파일명에 사용할 수 없는 문자 제거
safe_search = safe_search.replace(" ", "_")  # 공백을 언더스코어로 대체
safe_search = safe_search[:50]  # 파일명 길이 제한 (선택적)

current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"worknet_{safe_search}_{current_time}.csv"
file = open(filename, "w", encoding="utf-8", newline='')
writer = csv.writer(file)
writer.writerow([
    "회사명", "채용제목", "근로자수", "자본금", "연매출액", "주소", "지원URL", 
    "모집직종", "경력조건", "학력", "고용형태", "모집인원", "근무예정지", 
    "접수시작일", "접수마감일", "복리후생"
])

for job in jobs_db:
  writer.writerow(job.values())
        
print(f"채용정보가 {filename} 파일에 저장되었습니다.")

file.close()

