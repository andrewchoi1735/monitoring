import requests
from datetime import datetime

# 상수
BASE_URL = "https://othetak.com:8080"  # API의 기본 URL
LOGIN_URL = f"{BASE_URL}/v2/admin/sign/signIn"  # 로그인 API 엔드포인트
EMAIL_LOG_URL = f"{BASE_URL}/v2/admin/history/email"  # 이메일 로그 조회 API 엔드포인트
PUSHGATEWAY_URL = "http://localhost:9091/metrics/job/email_logs"

# 사용자 인증 정보
CREDENTIALS = {  # 로그인 시 필요한 사용자 ID와 비밀번호 설정
	"userId":"dychoi",  # 사용자 ID
	"password":"e123123!"  # 비밀번호
}

# 이메일 로그 조회 기본 파라미터
DEFAULT_PARAMS = {  # 이메일 로그 API에 전달할 기본 쿼리 파라미터
	"page":1,  # 요청할 페이지 번호
	"perPage":50,  # 한 페이지당 로그의 개수
	"typeCodeComma":"",  # 타입 코드 필터, 빈 문자열로 전체 조회
	"statusComma":0,  # 상태 필터 (0: 전체)
	"searchType":0,  # 검색 유형 필터 (0: 전체)
	"searchWord":""  # 검색어 필터, 빈 문자열로 전체 검색
}


def login_and_get_auth(session, payload):
	"""
    로그인 요청 및 인증 토큰과 쿠키 가져오기

    :param session: Session 객체 (requests.Session)
    :param payload: 로그인 요청에 필요한 사용자 ID와 비밀번호
    :return: Bearer Token과 Cookie (None, None 반환 가능)
    """
	try:
		# 로그인 요청
		response = session.post(LOGIN_URL, json=payload)  # 세션을 사용해 POST 요청을 보냄
		print("로그인 요청 상태 코드:", response.status_code)  # 상태 코드를 출력하여 요청 성공 여부를 확인

		if response.status_code == 200:  # 서버로부터 응답이 성공적으로 왔을 경우
			response_data = response.json()  # 응답을 JSON 형식으로 파싱
			# print("로그인 응답 데이터:", response_data)  # 디버깅용으로 데이터 출력

			# 로그인 성공 여부 판단
			if response_data.get("result"):  # 응답 데이터의 'result'가 True면 로그인 성공
				print("로그인 성공")

				# JWT 토큰 가져오기 (data 필드에서 토큰 추출)
				token = response_data.get("data")  # 응답 JSON의 data 필드에 Bearer Token이 포함됨

				# 세션에서 쿠키 가져오기 (서버가 반환한 세션 쿠키)
				cookies = session.cookies.get_dict()  # 세션에서 쿠키를 사전(dict) 형식으로 저장

				#print("Bearer Token:", token)  # 디버깅용으로 Bearer Token 출력
				#print("Cookies:", cookies)  # 디버깅용으로 쿠키 출력

				return token, cookies  # Bearer Token과 쿠키를 반환
			else:
				# 로그인 실패 시 메시지 출력
				print(f"로그인 실패 - 메시지: {response_data.get('message')}")
				return None, None  # 실패한 경우 None 반환
		else:
			# 서버로부터 기대하지 않은 상태 코드가 반환된 경우
			print(f"로그인 실패 - 상태 코드: {response.status_code}, 응답: {response.text}")
			return None, None  # 실패한 경우 None 반환
	except requests.exceptions.RequestException as e:
		# 요청 중 예외(Exception)가 발생한 경우 처리
		print(f"로그인 요청 중 오류 발생: {e}")
		return None, None  # 예외 발생 시 None 반환


def fetch_email_logs(session, token, cookies, params):
	"""
    이메일 로그 데이터 가져오기

    :param session: Session 객체 (requests.Session)
    :param token: Bearer Token (JWT 토큰)
    :param cookies: 로그인으로부터 획득한 쿠키(dict 형식)
    :param params: 이메일 로그 조회에 필요한 쿼리 파라미터
    :return: 이메일 로그 데이터 (JSON 형식) 또는 None
    """
	try:
		# 요청 헤더에 Bearer Token 추가
		headers = {
			"Authorization":f"Bearer {token}"  # Authorization 헤더에 토큰을 추가 (인증 목적으로 서버에 전달)
		}

		# 이메일 로그 데이터 조회 요청 (GET 메서드 사용)
		response = session.get(EMAIL_LOG_URL, headers=headers, cookies=cookies, params=params)
		print("이메일 로그 요청 상태 코드:", response.status_code)  # 상태 코드 출력

		if response.status_code == 200:  # 응답이 성공적일 경우
			# print("이메일 로그 응답 데이터:", response.json())  # 응답 JSON 데이터를 출력
			return response.json()  # 이메일 로그 데이터를 반환
		else:
			# 요청 실패 시 상태 코드와 에러 메시지 출력
			print(f"데이터 요청 실패 - 상태 코드: {response.status_code}, 응답: {response.text}")
			return None  # 실패한 경우 None 반환
	except requests.exceptions.RequestException as e:
		# 요청 중 예외(Exception)가 발생한 경우 처리
		print(f"데이터 요청 중 오류 발생: {e}")
		return None  # 예외 발생 시 None 반환


def send_to_pushgateway(logs, job_name, label_name):
	"""
    Pushgateway로 데이터를 일괄 전송하는 함수
    :param logs: 로그 리스트, 각 항목은 "send_datetime" 및 "error_message"를 포함
    :param job_name: Job 이름
    :param label_name: Label 이름
    """
	try:
		# 로그 개수 계산
		log_count = len(logs)

		# Pushgateway에 전송할 메트릭 데이터를 누적하여 작성
		metrics_data = f"""
# HELP email_logs_count 이메일 로그 총 개수
# TYPE email_logs_count gauge
email_logs_count{{job="{job_name}", label="{label_name}"}} {log_count}
"""

		for log in logs:
			send_datetime = log["sendDateTime"]
			error_message = log["errorMessage"]

			# send_datetime를 Unix 타임스탬프(float)로 변환
			send_datetime_unix = int(datetime.strptime(send_datetime, "%Y-%m-%dT%H:%M:%S").timestamp())

			# 메트릭 데이터 추가
			metrics_data += f"""
# HELP email_logs_send_datetime 최근 이메일 발송 시간 (Unix Timestamp)
# TYPE email_logs_send_datetime gauge
email_logs_send_datetime{{job="{job_name}", label="{label_name}"}} {send_datetime_unix}

# HELP email_logs_error_message_count 에러 메시지 발생 여부 (1이면 에러 발생, 0이면 정상)
# TYPE email_logs_error_message_count gauge
email_logs_error_message_count{{job="{job_name}", label="{label_name}"}} {1 if error_message else 0}
"""

		# Pushgateway로 POST 요청 (누적된 데이터를 한 번에 전송)
		response = requests.post(PUSHGATEWAY_URL, data=metrics_data)
		if response.status_code == 200:
			print(f"Pushgateway로 데이터 전송 성공! (총 {log_count}개의 로그)")
		else:
			print(f"Pushgateway 전송 실패: {response.status_code} - {response.text}")
	except ValueError as ve:
		print(f"날짜 변환 중 오류: {ve}")
	except requests.exceptions.RequestException as e:
		print(f"Pushgateway 전송 중 오류: {e}")


def main():
	"""
    메인 로직 실행
    """
	with requests.Session() as session:
		token, cookies = login_and_get_auth(session, CREDENTIALS)
		if token and cookies:
			data = fetch_email_logs(session, token, cookies, DEFAULT_PARAMS)
			if data and data.get("result"):
				# 이메일 로그 데이터에서 원하는 값 추출
				emaillog_list = data['data']['dataList']

				# Job 및 Label 이름 정의
				job_name = "email_logs_job"
				label_name = "email_failed_logs"

				# 데이터 전송 디버깅용 출력
				print(f"총 {len(emaillog_list)}개의 이메일 로그 데이터 처리 중...")

				# Pushgateway에 데이터 일괄 전송
				send_to_pushgateway(emaillog_list, job_name, label_name)
			else:
				print("이메일 로그 데이터를 가져오지 못했습니다.")
		else:
			print("로그인에 실패했습니다.")


if __name__ == "__main__":
	main()
