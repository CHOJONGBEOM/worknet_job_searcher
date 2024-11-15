from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re


def crawling(page, context):
  jobs_db = []
  current_page = 1
  total_result = int(page.locator("h3 .hit strong").inner_text())
  total_page = (total_result + 49) // 50  # 50으로 나누어 올림

  while current_page <= total_page:
    content = page.content()
    soup = BeautifulSoup(content, 'html.parser')
    # 공고별 열고 닫기
    links = page.query_selector_all('a.t3_sb.underline_hover')
    for link in links:
      url = link.get_attribute('href')
      if url:
        try:
          new_page = context.new_page()
          new_page.goto(url, wait_until="networkidle")
          content = new_page.content()
          soup = BeautifulSoup(content, "html.parser")
          #크롤링 정보 입력
          job = soup.find("div", class_="careers-area")
          
          try:
            #회사명
            company_name = job.find('p',class_='name').get_text(strip=True, separator=' ')
            #채용제목
            job_title = job.find('p',class_='title').get_text(strip=True, separator=' ')
            #근로자수
            worker_count = job.find("th", text="근로자수").find_next("td").get_text(strip=True, separator=' ')
            #자본금
            capital = job.find("th", text="자본금").find_next("td").get_text(strip=True, separator=' ')
            #연매출액
            annual_revenue = job.find("th", text="연매출액").find_next("td").get_text(strip=True, separator=' ')
            #주소
            location = job.find("th", string="주소").find_next("td").get_text(strip=True, separator=' ')
            location = re.sub(r'\s+', ' ', location)
            #지원url
            apply_url = job.find("th", text="홈페이지").find_next("td").find("a").get("href")

            # 첫 번째 테이블 처리 (경력조건, 학력, 고용형태, 모집인원, 근무예정지)
            result = {}
            if soup.find('caption', text="경력조건, 학력, 고용형태, 모집인원, 근무예정지 표"):
              table1 = soup.find('caption', text="경력조건, 학력, 고용형태, 모집인원, 근무예정지 표").parent
              headers1 = [th.get_text(strip=True) for th in table1.select('thead th')]
              row_data1 = [td.get_text(strip=True) for td in table1.select('tbody td')]
              cleaned_row_data1 = [re.sub(r'\s+', ' ', data.strip()) for data in row_data1]
              result.update(dict(zip(headers1, cleaned_row_data1)))
            else:
              pass

            # 두 번째 테이블 처리 (직무내용, 모집직종)
            if soup.find('caption', text="직무내용, 모집직종 표"):
              table2 = soup.find('caption', text="직무내용, 모집직종 표").parent
              headers2 = [th.get_text(strip=True) for th in table2.select('thead th')]
              row_data2 = [td.get_text(strip=True) for td in table2.select('tbody td')]
              cleaned_row_data2 = [re.sub(r'\s+', ' ', data.strip()) for data in row_data2]
              result.update(dict(zip(headers2, cleaned_row_data2)))
            else:
              pass
            

            # 세 번째 테이블 처리 (근무환경 및 복리후생)
            if soup.find('caption', text="근무환경 및 복리후생"):
              table3 = soup.find('caption', text="근무환경 및 복리후생").parent
              headers3 = [th.get_text(strip=True) for th in table3.select('thead th')]
              row_data3 = [td.get_text(strip=True) for td in table3.select('tbody td')]
              cleaned_row_data3 = [re.sub(r'\s+', ' ', data.strip()) for data in row_data3]
              result.update(dict(zip(headers3, cleaned_row_data3)))
            else:
              pass

            # 네 번째 테이블 처리 (모집직종, 경력조건, 학력, 고용형태, 모집인원, 근무예정지 표)
            if soup.find('caption', text="모집직종, 경력조건, 학력, 고용형태, 모집인원, 근무예정지 표"):
              table4 = soup.find('caption', text="모집직종, 경력조건, 학력, 고용형태, 모집인원, 근무예정지 표").parent
              headers4 = [th.get_text(strip=True) for th in table4.select('thead th')]
              row_data4 = [td.get_text(strip=True) for td in table4.select('tbody td')]
              cleaned_row_data4 = [re.sub(r'\s+', ' ', data.strip()) for data in row_data4]
              result.update(dict(zip(headers4, cleaned_row_data4)))
            else:
              pass

            #복리후생
            welfare = result.get("복리후생", "정보없음")
            #경력
            career = result.get("경력조건", "정보없음")
            #모집직종
            job_category = result.get("모집직종", "정보없음")
            #학력
            education = result.get("학력", "정보없음")
            #고용형태
            employment_type = result.get("고용형태", "정보없음")
            #모집인원
            hire_number = result.get("모집인원", "정보없음")
            #근무예정지
            work_location = result.get("근무예정지", "정보없음")

            date_info = job.find("th", text="접수마감일").find_next("td").get_text(strip=True, separator=' ')
            date_info = re.sub(r'\s+', ' ', date_info)
            start_date = "정보없음"
            end_date = "정보없음"

            start_match = re.search(r'접수시작일\s*:\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)', date_info)
            if start_match:
              start_date = start_match.group(1)

            end_match = re.search(r'접수마감일\s*:\s*(\d{4}년\s*\d{1,2}월\s*\d{1,2}일)', date_info)
            if end_match:
              end_date = end_match.group(1)
            else:
              # 접수마감일이 없는 경우 접수마감유형 확인
              if "상시" in date_info:
                  end_date = "상시"
              elif "채용시까지" in date_info:
                  end_date = "채용시까지"
            
            #복리후생
            welfare = result.get("복리후생", "정보없음")

            job_info = {
              "company_name": company_name,
              "job_title": job_title,
              "employee_count": worker_count,
              "capital": capital,
              "annual_revenue": annual_revenue,
              "address": location,
              "apply_url": apply_url,
              "job_category": job_category,
              "career_requirement": career,
              "education_requirement": education,
              "employment_type": employment_type,
              "number_of_recruits": hire_number,
              "work_location": work_location,
              "application_start_date": start_date,
              "application_end_date": end_date,
              "welfare": welfare
            }

            jobs_db.append(job_info)
          except:
            pass
        finally:
          new_page.close()
    if current_page < total_page:

      #다음 페이지로 이동
      next_page = current_page + 1
      next_page_str = str(next_page)
      next_button = soup.find('button', class_='btn_page next')

      #다음 페이지 버튼이 있는지 없는지에 따른 처리
      try:
        if current_page % 10 == 0:
          print(f"페이지 {current_page}에서 다음 버튼 클릭")
          page.click('button.btn_page.next')
        else:
          print(f"페이지 {current_page}에서 {next_page}로 이동 시도")
          page.get_by_role("button", name=next_page_str).click()

        page.wait_for_load_state('networkidle', timeout=120000)
        current_page = next_page
      except:
        print("페이지 이동중 오류 발생")
    else:
      print("마지막 페이지 크롤링 완료")
      break

  return jobs_db
  