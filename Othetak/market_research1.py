import datetime
import time
from playwright.sync_api import Playwright, sync_playwright
import sys


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


# 시장조사 작성 내역 확인
def market_search_list_check(page):
	selector1 = "body > div.font-wrapper.container > div.content > div > h1"
	check_header = page.locator(selector1)
	if not check_header.is_visible():  # 만약 헤더가 없다면 화면이 에러난거임
		print("화면 에러")
		return
	selector2 = "body > div.font-wrapper.container > div.content > div > div.table-filter > div > div.total-count-wrapper > span.total-count > span"
	total_count = page.locator(selector2).inner_text()

	if total_count == "0":
		print("저장된 작성 내역이 없음")
	# 작성된 내역이 있는경우, 가장 최근의 항목에 대한 정보 긁어오기
	else:
		print(f"저장된 작성 내역 : 총 {total_count}건")
		row_selector = "body > div.font-wrapper.container > div.content > div > div.table-wrapper > div > div > table > tbody > tr:nth-child(1)"
		table_row = page.locator(row_selector)

		columns = table_row.locator("td").all_inner_texts()
		column_data = [column.strip() for column in columns]

		selected_data = [column_data[i] for i in [2, 3, 4, 8, 9, 11, 12] if i < len(column_data)]

		print(selected_data)

		return selected_data


def move_research_detail(page):
	page.locator(
		"body > div.font-wrapper.container > div.content > div > div.table-wrapper > div > div > table > tbody > tr:nth-child(1)").click()


def match_check(page, retries=5):
	match_status_selector = "body > div.font-wrapper.container > div.content > div > div.table-wrapper > div > div > table > tbody > tr:nth-child(1) > td.MuiTableCell-root.MuiTableCell-body.MuiTableCell-alignCenter.MuiTableCell-sizeMedium.css-1201061"
	match_status = page.locator(match_status_selector).inner_text()

	if match_status == "매칭 완료":
		move_research_detail(page)
		time.sleep(10)
		try:
			# "AI 추천" 요소를 모두 가져와 확인
			ai_recommendation_elements = page.locator("text=AI 추천")
			for i in range(ai_recommendation_elements.count()):
				if ai_recommendation_elements.nth(i).is_visible():
					print("true")
					return True
				else:
					print("false")
					return False

		except Exception as e:
			print("false")
			return False
	elif match_status == "진행중":
		if retries > 0:  # 반복 횟수 제한
			print(f"매칭이 진행중입니다. 50초 후 다시 확인합니다. 남은 시도 횟수: {retries}")
			page.reload()
			time.sleep(20)
			return match_check(page, retries=retries - 1)
		else:
			print("매칭 시도가 실패했습니다.")
			return False

	else:
		sys.exit(-1)


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

	time.sleep(10)

	page.reload()

	# 매칭 진행 후, 내역 화면 이니, 이 때, 가장 최신의 파일이 매칭 완료 되었는지 확인
	try:
		page.wait_for_selector(
			"body > div.font-wrapper.container > div.content > div > div.table-wrapper > div > div > table > tbody > tr:nth-child(1)",
			timeout=1000)
	except Exception as e:
		print(f"error: {e}")
		return
	match_check(page, retries=5)


with sync_playwright() as test:
	run(test)
