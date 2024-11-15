
from playwright.sync_api import sync_playwright


def browser(url, search):
  p = sync_playwright().start()
  browser = p.chromium.launch(headless=False, args=['--start-maximized'])
  context = browser.new_context()
  page = browser.new_page()
  page.goto(url, wait_until='networkidle')
  page.get_by_placeholder("여러단어를 입력하실 때는 띄어쓰기(AND), |(OR) 연산자를 이용하여 더욱 세밀하게 검색 가능합니다.").fill(search)
  page.click('button[onclick="fn_Search(\'1\');"]')
  page.wait_for_load_state('networkidle')
  page.locator('select[title="리스트보기 개수를 선택해 주세요"]').click()
  page.select_option('select[title="리스트보기 개수를 선택해 주세요"]', value='50')
  page.click('button[onclick="fn_Search(1);"]')
  page.wait_for_load_state('networkidle')

  return page, context

