import requests
from datetime import datetime

# 상수
BASE_URL = "https://othetak.com:8080"  # API의 기본 URL
LOGIN_URL = f"{BASE_URL}/v2/admin/sign/signIn"  # 로그인 API 엔드포인트
SMS_LOG_API = f"{BASE_URL}/admin/sms/smsCount"  # SMS 로그 조회 API 엔드포인트
PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/smsCount"  # Pushgateway URL

# 사용자 인증 정보
CREDENTIALS = {  # 로그인 시 필요한 사용자 ID와 비밀번호 설정
	"userId":"dychoi",  # 사용자 ID
	"password":"e123123!"  # 비밀번호
}



def login_and_get_auth(session, payload):
	"""
    로그인 요청 및 인증 토큰과 쿠키 가져오기
    """
	try:
		# 로그인 요청
		response = session.post(LOGIN_URL, json=payload)
		print("로그인 요청 상태 코드:", response.status_code)

		if response.status_code == 200:
			response_data = response.json()

			if response_data.get("result"):
				print("로그인 성공")
				token = response_data.get("data")
				cookies = session.cookies.get_dict()
				return token, cookies
			else:
				print(f"로그인 실패 - 메시지: {response_data.get('message')}")
				return None, None
		else:
			print(f"로그인 실패 - 상태 코드: {response.status_code}, 응답: {response.text}")
			return None, None
	except requests.exceptions.RequestException as e:
		print(f"로그인 요청 중 오류 발생: {e}")
		return None, None


def fetch_sms_count(session, token, cookies):
	"""
    SMS 카운트 데이터 가져오기
    """
	try:
		headers = {
			"Authorization":f"Bearer {token}"
		}

		response = session.get(SMS_LOG_API, headers=headers, cookies=cookies)
		print("SMS count 상태 코드:", response.status_code)

		if response.status_code == 200:
			return response.json()
		else:
			print(f"데이터 요청 실패 - 상태 코드: {response.status_code}, 응답: {response.text}")
			return None
	except requests.exceptions.RequestException as e:
		print(f"데이터 요청 중 오류 발생: {e}")
		return None


def send_to_pushgateway(sms, lms, mms, stat):
	"""
    Pushgateway로 데이터를 전송하는 함수
    """
	try:
		# Pushgateway에 전송할 메트릭 데이터를 Prometheus 포맷에 맞게 작성
		metrics_data = f"""
# HELP remaining_sms_count SMS 남은 건수
# TYPE remaining_sms_count gauge
remaining_sms_count {sms}

# HELP remaining_lms_count LMS 남은 건수
# TYPE remaining_lms_count gauge
remaining_lms_count {lms}

# HELP remaining_mms_count MMS 남은 건수
# TYPE remaining_mms_count gauge
remaining_mms_count {mms}

# HELP server_status 상태 코드 (정상: 0, 문제: -1)
# TYPE server_status gauge
server_status {stat}
"""

		# Pushgateway로 전송 (POST)
		response = requests.post(PUSHGATEWAY_URL, data=metrics_data)
		if response.status_code == 200:
			print("Pushgateway로 메트릭 데이터 전송 성공!")
		else:
			print(f"Pushgateway 전송 실패: {response.status_code} - {response.text}")
	except requests.exceptions.RequestException as e:
		print(f"Pushgateway 전송 중 오류 발생: {e}")


def process_sms_data(data):
	"""
    SMS 데이터를 처리하여 서버 상태를 결정
    """
	sms = data.get("sms", 0)
	lms = data.get("lms", 0)
	mms = data.get("mms", 0)

	# 서버 상태 처리 ("-"이 하나라도 있으면 서버 문제)
	if sms == "-" or lms == "-" or mms == "-":
		print("서버 문제 발생: SMS, LMS, MMS에 '-' 값이 포함됨")
		server_stat = -1
		sms = 0
		lms = 0
		mms = 0
	else:
		print("서버 정상: SMS, LMS, MMS 값이 올바른 숫자")
		server_stat = 0

	return sms, lms, mms, server_stat


def main():
	"""
    메인 로직 실행
    """
	with requests.Session() as session:
		token, cookies = login_and_get_auth(session, CREDENTIALS)
		if token and cookies:
			data = fetch_sms_count(session, token, cookies)
			if data and data.get("result"):
				# SMS 데이터를 처리
				sms_data = data["data"]
				sms, lms, mms, server_stat = process_sms_data(sms_data)

				print(f"SMS: {sms}, LMS: {lms}, MMS: {mms}, 서버 상태: {server_stat}")

				# Pushgateway로 데이터 전송
				send_to_pushgateway(sms, lms, mms, server_stat)
			else:
				print("SMS 데이터를 가져오지 못했습니다.")
		else:
			print("로그인에 실패했습니다.")


if __name__ == "__main__":
	main()
