import datetime
import time
from playwright.sync_api import Playwright, sync_playwright


# 시장조사 등록 화면 이동
def move_add_market_search(page):
	page.get_by_role("link", name="시장조사 AI").click()
	time.sleep(2)


# 파일 업로드
def market_file_upload(page):
	file_path = r"C:\Users\doyun\Downloads\동광중(24.10.08) AI시장조사_가격삭제.xlsx"

	input_elements = page.query_selector_all("input")
	for input_el in input_elements:
		if input_el.get_attribute("type") == "file":
			input_el.set_input_files(file_path)
			break
	time.sleep(1)

	upload_check = "body > div.font-wrapper.container > div.content > div > div.ag-theme-alpine > div > div > table > tbody > tr:nth-child(1)"
	if page.locator(upload_check).is_visible():
		return True
	else:
		print("뭔가 잘못됐는데여?")


# AI 매칭 진행
def market_search_AI_match(page):
	# 파일 업로드
	market_file_upload(page)

	# AI 매칭
	match_button = "body > div.font-wrapper.container > div.content > div > div:nth-child(3) > div.rightWrapper > button"
	page.locator(match_button).click()
	time.sleep(1)
	# 전체 선택
	all_check = "body > div.MuiModal-root.css-1sucic7 > div.css-xna42m > div.css-gmqetk > div > label"
	page.locator(all_check).click()
	time.sleep(0.5)
	# 매칭 버튼 클릭
	page.locator(
		"body > div.MuiModal-root.css-1sucic7 > div.css-xna42m > div:nth-child(4) > button.css-1xdk21t").click()
	time.sleep(0.5)
	# 매칭 진행 여부 팝업
	if page.locator("body > div.MuiModal-root.css-1sucic7 > div.MuiBox-root.css-8kenvv > div").is_visible():
		page.locator(
			"body > div.MuiModal-root.css-1sucic7 > div.MuiBox-root.css-8kenvv > div > div.alert__btn-wrapper > button.css-1xdk21t").click()
	else:
		print("뭔가 잘못됐는데여?")


def check_move_to_list(page):
	selector = "body > div.font-wrapper.container > div.content > div > h1"
	title = page.locator(selector).inner_text()

	if title == "시장조사 작성 내역":
		print("AI 매칭 정상 처리 확인")
		return True
	else:
		return False


def othetak_login(page):
	page.get_by_placeholder("아이디").fill("andrewchoi")
	page.get_by_placeholder("비밀번호").fill("ee123123")
	page.wait_for_timeout(350)
	page.locator("form").get_by_role("button", name="로그인", exact=True).click()
	time.sleep(1)


def run(playwright: Playwright) -> None:
	# 브라우저를 고정된 창 크기로 시작
	browser = playwright.chromium.launch(headless=False)
	context = browser.new_context()
	page = context.new_page()

	# goto 해당 URL로 접속하기.
	page.goto("https://othetak.com/auth/signIn")
	time.sleep(1)

	# 로그인 진행
	othetak_login(page)

	# 시장조사 등록 화면 이동
	move_add_market_search(page)

	# AI 매칭 진행
	market_search_AI_match(page)

	time.sleep(5)

	check_move_to_list(page)


with sync_playwright() as test:
	run(test)
