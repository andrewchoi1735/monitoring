import requests

# 로그인 URL
LOGIN_URL = "https://api.othetak.com:8080/v2/sign/signIn"

# 로그인 자격 증명
credentials = {
	"userId":"andrewchoi",  # 사용자 ID
	"password":"ee123123"  # 비밀번호
}

# 전역 변수 - 추출된 AccessToken
access_token = None


def login():
	"""로그인 요청 및 액세스 토큰 추출"""
	global access_token
	try:
		# 로그인 요청
		response = requests.post(LOGIN_URL, json=credentials)

		# 응답 상태 코드 및 내용 출력
		print("응답 상태 코드:", response.status_code)
		print("응답 내용:", response.text)

		# 200 상태 코드 처리
		if response.status_code == 200:
			data = response.json()
			# 로그인 성공 시 AccessToken 추출
			if data.get("result") and data.get("data"):
				access_token = data["data"]
				print("로그인 성공! AccessToken:", access_token)
			else:
				print(f"로그인 실패: {data.get('message') or '알 수 없는 오류'}")
		else:
			print(f"로그인 요청 실패. 상태 코드: {response.status_code}, 메시지: {response.text}")
	except Exception as e:
		print(f"로그인 요청 중 오류 발생: {e}")


def fetch_protected_data():
	"""AccessToken을 사용해 인증이 필요한 데이터를 요청"""
	global access_token
	if not access_token:
		print("AccessToken이 없습니다. 먼저 로그인하십시오.")
		return

	# 보호된 리소스 URL
	protected_url = "https://api.othetak.com:8080/v2/protected/resource"

	# Authorization 헤더에 AccessToken 포함
	headers = {
		"Authorization":f"Bearer {access_token}"
	}

	try:
		# 데이터 요청
		response = requests.get(protected_url, headers=headers)
		print("보호된 데이터 응답 상태 코드:", response.status_code)
		print("보호된 데이터 응답 내용:", response.text)

		if response.status_code == 200:
			data = response.json()
			print("보호된 데이터 요청 성공:", data)
		else:
			print(f"보호된 데이터 요청 실패: {response.status_code}, {response.text}")
	except Exception as e:
		print(f"보호된 데이터 요청 중 오류 발생: {e}")


if __name__ == "__main__":
	# 1. 로그인
	login()

	# 2. AccessToken이 있는 경우 보호된 데이터 요청
	if access_token:
		fetch_protected_data()
