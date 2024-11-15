
![워크넷 스크래퍼 검색결과2](https://github.com/user-attachments/assets/0908e3ee-6178-4f4e-b01e-19b84a8124c7)

# 워크넷 채용정보 크롤러

이 프로젝트는 워크넷 웹사이트에서 채용 정보를 크롤링하고 CSV 파일로 저장하는 Python 애플리케이션입니다.

### 300개 이상의 데이터를 수집 시 오랜 시간이 걸릴 수 있습니다 (15분 이상)

## 기능

- 워크넷 웹사이트에서 키워드 기반 채용 정보 검색
- 검색 결과 크롤링 및 상세 정보 추출
- 결과를 CSV 파일로 저장

## 파일 구조

- `worknet_search.py`: 메인 GUI 애플리케이션
- `worknet_crawling.py`: 크롤링 로직
- `worknet_browser.py`: 브라우저 설정 및 초기화
- `main.py`: 커맨드 라인 실행용 스크립트

## 요구 사항

이 애플리케이션을 실행하기 위해서는 다음의 Python 라이브러리가 필요합니다:

- PyQt5
- BeautifulSoup4
- Playwright


## 설치 및 실행 방법

### 1. Python 설치 확인

1. **Python 설치 확인**:
   - Windows에서 명령 프롬프트를 열고 다음 명령어를 입력하여 Python이 설치되어 있는지 확인합니다.
     ```cmd
     python --version
     ```
   - Python 버전이 출력되면 설치가 완료된 것입니다. 그렇지 않다면 [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드하여 설치하세요.


### 2. 소스 코드 다운로드

1. **소스 코드 다운로드**:
   - 프로젝트 파일들(worknet_search.py, worknet_crawling.py, worknet_browser.py, main.py)을 동일한 디렉토리에 저장합니다.

### 3. 실행 파일 생성

이 프로그램을 실행 가능한 `.exe` 파일로 만들기 위해, 다음 단계를 따르세요.

1. **필요한 라이브러리 설치**:
   - 다음 명령어를 입력하여 라이브러리를 설치합니다
     ```cmd
     pip install PyQt5 beautifulsoup4 playwright pyinstaller
     ```

2. **Playwright 브라우저 설치**:
     ```cmd
     playwright install
     ```
     
3. **PyInstaller로 실행 파일 생성**:
   - 코드가 저장된 디렉토리로 이동한 후 다음 명령어를 실행합니다.
     ```cmd
     pyinstaller --onefile --windowed --collect-all playwright worknet_search.py
     ```
     
5. **실행 파일 실행**:
   - dist 폴더 안의 worknet_search.exe 파일을 더블클릭하여 실행합니다.
   - 1. GUI 창이 열리면, 검색어를 입력하고 "검색" 버튼을 클릭합니다.
     2. 검색이 완료되면 결과가 `worknet_{검색어}_{날짜}.csv` 파일로 저장됩니다.
