import requests
from datetime import datetime
# 상수
BASE_URL = "https://api.othetak.com:8080"
LOGIN_URL = f"{BASE_URL}/v2/sign/signIn"
DATA_URL = f"{BASE_URL}/v2/guest/goods/integrated-landing-record"

# 날짜
today_date = datetime.now().strftime("%Y-%m-%d")


# 로그인 정보
payload = {
	"userId":"monitor2",
	"password":"qwer1234!@#$"
}

# 데이터 요청 파라미터
params = {
	"sortBasisCode":"",
	"perPage":100,
	"priceBasisDate":today_date,
	"distributionSpecialtyName":"",
	"storeName":"",
	"goodsName":"",
	"ingredientAndContent":"",
	"standards":"",
	"page":1
}


def fetch_data_with_login():
	try:
		session = requests.Session()

		# 로그인 요청
		login_response = session.post(LOGIN_URL, json=payload)
		print("로그인 응답 상태 코드:", login_response.status_code)
		print("로그인 응답 데이터:", login_response.text)

		# 로그인 성공 여부 확인
		response_data = login_response.json()
		if login_response.status_code == 200 and response_data.get("result") is True:
			print("로그인 성공")
		else:
			print(f"로그인 실패 - 메시지: {response_data.get('message')}")
			return

		# 데이터 요청
		response = session.get(DATA_URL, params=params)
		print("데이터 응답 상태 코드:", response.status_code)
		if response.status_code == 200:
			data = response.json()
			# 데이터 유효성 검사
			if "data" in data and "goodsIntegrated" in data["data"]:
				items = data["data"]["goodsIntegrated"]
				item_count = len(items)
				print(f"Total number of items: {item_count}")
				push_to_prometheus(item_count)
			else:
				print("Unexpected response structure:", data)
		else:
			print(f"데이터 요청 실패: {response.text}")

	except requests.exceptions.RequestException as e:
		print(f"요청 중 오류 발생: {e}")
	except Exception as e:
		print(f"알 수 없는 오류 발생: {e}")


def push_to_prometheus(count):
	url = "http://localhost:9091/metrics/job/goods_seoul"
	data = f"count {count}\n"
	response = requests.post(url, data=data)
	return response.status_code

if __name__ == "__main__":
	fetch_data_with_login()
