import requests

LOGIN_URL = "https://api.othetak.com:8080/v2/sign/signIn"
CHECK_URL = "https://othetak.com/goods/comparison"

# 로그인 시 필요한 데이터 (로그인 폼에 입력되는 데이터)
payload = {
	"username":"andrewchoi",
	"password":"ee123123"
}

# 세션 유지
session = requests.Session()

try:
	# 로그인 요청
	login_response = session.post(LOGIN_URL, json=payload)
	if login_response.status_code == 200:
		print("로그인 성공")

		# 로그인 후 대상 페이지 상태 확인
		response = session.get(CHECK_URL)

		if response.status_code == 200:
			print("대상 웹페이지가 정상적으로 작동하고 있습니다.")
		else:
			print("대상 웹페이지에 문제가 있습니다. 상태 코드:", response.status_code)
	else:
		print("로그인 실패. 상태 코드:", login_response.status_code)

except requests.exceptions.RequestException as e:
	print("요청 중 문제가 발생했습니다. 에러:", e)
