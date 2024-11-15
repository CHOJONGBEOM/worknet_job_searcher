import sys
import csv
import datetime
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

class ScraperThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)

    def __init__(self, search):
        super().__init__()
        self.search = search

    def run(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                url = "https://www.work24.go.kr/wk/a/b/1200/retriveDtlEmpSrchList.do?staArea=&programMenuIdentification=EBG020000000002&indArea="
                page.goto(url, wait_until='networkidle')
                page.get_by_placeholder("여러단어를 입력하실 때는 띄어쓰기(AND), |(OR) 연산자를 이용하여 더욱 세밀하게 검색 가능합니다.").fill(self.search)
                page.click('button[onclick="fn_Search(\'1\');"]')
                page.wait_for_load_state('networkidle')
                page.locator('select[title="리스트보기 개수를 선택해 주세요"]').select_option('50')
                page.click('button[onclick="fn_Search(1);"]')
                page.wait_for_load_state('networkidle')

                jobs_db = []
                current_page = 1
                total_result = int(page.locator("h3 .hit strong").inner_text())
                total_page = (total_result + 49) // 50  # 50으로 나누어 올림

                while current_page <= total_page:
                    self.update_signal.emit(f"페이지 {current_page}/{total_page} 크롤링 중...")
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    links = page.query_selector_all('a.t3_sb.underline_hover')

                    for link in links:
                        url = link.get_attribute('href')
                        if url:
                            try:
                                new_page = browser.new_page()
                                new_page.goto(url, wait_until="networkidle")
                                content = new_page.content()
                                soup = BeautifulSoup(content, "html.parser")
                                job = soup.find("div", class_="careers-area")
                                try:
                                    company_name = job.find('p', class_='name').get_text(strip=True, separator=' ')
                                    job_title = job.find('p', class_='title').get_text(strip=True, separator=' ')
                                    worker_count = job.find("th", text="근로자수").find_next("td").get_text(strip=True, separator=' ')
                                    capital = job.find("th", text="자본금").find_next("td").get_text(strip=True, separator=' ')
                                    annual_revenue = job.find("th", text="연매출액").find_next("td").get_text(strip=True, separator=' ')
                                    location = job.find("th", string="주소").find_next("td").get_text(strip=True, separator=' ')
                                    location = re.sub(r'\s+', ' ', location)
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

                                    welfare = result.get("복리후생", "정보없음")
                                    career = result.get("경력조건", "정보없음")
                                    job_category = result.get("모집직종", "정보없음")
                                    education = result.get("학력", "정보없음")
                                    employment_type = result.get("고용형태", "정보없음")
                                    hire_number = result.get("모집인원", "정보없음")
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
                                        if "상시" in date_info:
                                            end_date = "상시"
                                        elif "채용시까지" in date_info:
                                            end_date = "채용시까지"

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
                            except Exception as e:
                                self.update_signal.emit(f"Error processing job: {str(e)}")
                                pass
                            finally:
                                new_page.close()

                    if current_page < total_page:
                        next_page = current_page + 1
                        try:
                            if current_page % 10 == 0:
                                page.click('button.btn_page.next')
                            else:
                                page.get_by_role("button", name=str(next_page)).click()
                            page.wait_for_load_state('networkidle', timeout=120000)
                            current_page = next_page
                        except:
                            self.update_signal.emit("페이지 이동 중 오류 발생")
                            pass
                    else:
                        self.update_signal.emit("마지막 페이지 크롤링 완료")
                        break

                browser.close()
                self.finished_signal.emit(jobs_db)

        except Exception as e:
            self.update_signal.emit(f"오류 발생: {str(e)}")

class WorknetSearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('워크넷 직무 검색')
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        search_button = QPushButton('검색')
        search_button.clicked.connect(self.start_search)

        input_layout.addWidget(QLabel('검색어:'))
        input_layout.addWidget(self.keyword_input)
        input_layout.addWidget(search_button)

        layout.addLayout(input_layout)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def start_search(self):
        keyword = self.keyword_input.text()
        if not keyword:
            self.result_text.setText("검색어를 입력해주세요.")
            return

        self.result_text.clear()
        self.result_text.append(f"'{keyword}' 검색을 시작합니다...")

        self.scraper_thread = ScraperThread(keyword)
        self.scraper_thread.update_signal.connect(self.update_progress)
        self.scraper_thread.finished_signal.connect(self.save_results)
        self.scraper_thread.start()

    def update_progress(self, message):
        self.result_text.append(message)

    def save_results(self, jobs_db):
        if not jobs_db:
            self.result_text.append("\n검색 결과가 없습니다.")
            return

        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 검색어 처리 - text() 메서드 호출로 수정
        search_term = self.keyword_input.text().strip()
        safe_search_term = re.sub(r'[\\/*?:"<>|]', "", search_term)
        safe_search_term = safe_search_term.replace(" ", "_")
        safe_search_term = safe_search_term[:50]
        
        file_name = f"worknet_{safe_search_term}_{current_time}.csv"
        
        fieldnames = [
            "company_name", "job_title", "employee_count", "capital", 
            "annual_revenue", "address", "apply_url", "job_category",
            "career_requirement", "education_requirement", "employment_type",
            "number_of_recruits", "work_location", "application_start_date",
            "application_end_date", "welfare"
        ]
        
        headers = [
            "회사명", "채용제목", "근로자수", "자본금", "연매출액", "주소", "지원URL", 
            "모집직종", "경력조건", "학력", "고용형태", "모집인원", "근무예정지", 
            "접수시작일", "접수마감일", "복리후생"
        ]

        # 데이터 검증
        try:
            with open(file_name, "w", encoding="utf-8-sig", newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writerow(dict(zip(fieldnames, headers)))  # 한글 헤더 작성

                for job in jobs_db:
                    # 각 필드가 있는지 확인하고 없으면 기본값 설정
                    row_dict = {}
                    for field in fieldnames:
                        row_dict[field] = job.get(field, "정보없음")
                    writer.writerow(row_dict)

            self.result_text.append(f"\n총 {len(jobs_db)}개의 채용정보가 다음 파일에 저장되었습니다:\n{file_name}")
        except PermissionError:
            self.result_text.append("\n파일이 다른 프로그램에서 사용 중입니다. 파일을 닫고 다시 시도해주세요.")
        except Exception as e:
            self.result_text.append(f"\n파일 저장 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WorknetSearchApp()
    ex.show()
    sys.exit(app.exec_())