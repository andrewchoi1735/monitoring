import re
import requests

# 상수
BASE_URL = "https://api.othetak.com:8080"
LOGIN_URL = f"{BASE_URL}/v2/sign/signIn"
DATA_URL = f"{BASE_URL}/main/goods3rd"
PROMETHEUS_BASE_URL = "http://localhost:9091/metrics/job/goods3rd"

# 로그인 정보 목록 (비로그인 포함)
regions = [
	{"region":"guest", "userId":None, "password":None},  # 비로그인
	{"region":"seoul", "userId":"monitor3", "password":"qwer1234!@#$"},
	{"region":"incheon", "userId":"monitor1", "password":"qwer1234!@#$"},
	{"region":"dajeon", "userId":"monitor5", "password":"qwer1234!@#$"},
	{"region":"jeju", "userId":"monitor4", "password":"qwer1234!@#$"},
	{"region":"sejong", "userId":"monitor2", "password":"qwer1234!@#$"},
]


def sanitize_metric_name(name):
	"""
    Prometheus 메트릭 이름 규칙에 맞게 변환:
    - 소문자만 사용, 공백/특수문자 제거, 대문자는 소문자로 변환
    """
	name = name.lower()
	name = re.sub(r'[^a-z0-9_]', '_', name)  # 알파벳, 숫자, 밑줄 이외는 밑줄로 변경
	return name


def fetch_data_with_login(region, userId=None, password=None):
	"""
    특정 계정/지역에 대해 데이터를 가져온 후 Prometheus로 전송.
    """
	try:
		session = requests.Session()
		token = None

		# 로그인 과정
		if userId and password:
			payload = {"userId":userId, "password":password}
			login_response = session.post(LOGIN_URL, json=payload)
			print(f"[{region}] 로그인 응답 상태 코드: {login_response.status_code}")
			print(f"[{region}] 로그인 응답 데이터: {login_response.text}")

			response_data = login_response.json()
			if login_response.status_code == 200 and response_data.get("result") is True:
				token = response_data.get("token")
				print(f"[{region}] 로그인 성공")
			else:
				print(f"[{region}] 로그인 실패: {response_data.get('message')}")
				return
		else:
			print(f"[{region}] 비로그인 접근")

		# 데이터 요청
		headers = {"Authorization":f"Bearer {token}"} if token else {}
		response = session.get(DATA_URL, headers=headers)
		print(f"[{region}] 데이터 응답 상태 코드: {response.status_code}")
		print(f"[{region}] 데이터 응답 본문: {response.text}")

		if response.status_code == 200:
			data = response.json()
			if "data" in data and isinstance(data["data"], dict):
				section_counts = {key:len(items) for key, items in data["data"].items()}
				print(f"[{region}] 섹션별 아이템 개수: {section_counts}")
				push_sections_to_prometheus(region, section_counts)
			else:
				print(f"[{region}] 데이터 구조가 예상과 다릅니다. 응답 데이터: {data}")
		else:
			print(f"[{region}] 데이터 요청 실패: {response.text}")

	except requests.exceptions.RequestException as e:
		print(f"[{region}] 요청 중 오류 발생: {e}")
	except Exception as e:
		print(f"[{region}] 알 수 없는 오류 발생: {e}")


def push_sections_to_prometheus(region, section_counts):
	"""
    Prometheus PushGateway에 섹션별 데이터 개수 푸시
    """
	url = PROMETHEUS_BASE_URL  # URL 수정
	prometheus_data = ""  # 전송할 모든 데이터를 누적

	for section, count in section_counts.items():
		sanitized_section = sanitize_metric_name(section)  # 메트릭 이름 정리
		metric_name = f"{sanitized_section}_count"  # 메트릭 이름 구성
		# 라벨(region)을 포함한 데이터 형식 구성
		prometheus_data += f'{metric_name}{{region="{region}"}} {count}\n'

	print(f"[{region}] 전송 데이터:\n{prometheus_data}")

	try:
		# PushGateway로 전송
		response = requests.post(url, data=prometheus_data)
		if response.status_code == 200:
			print(f"[{region}] Prometheus 전송 성공")
		else:
			print(f"[{region}] Prometheus 전송 실패 - 상태 코드: {response.status_code}")
			print(f"[{region}] 전송 실패 응답 메시지: {response.text}")
	except requests.exceptions.RequestException as e:
		print(f"[{region}] Prometheus 전송 중 오류 발생: {e}")


if __name__ == "__main__":
	for region_info in regions:
		fetch_data_with_login(
			region=region_info["region"],
			userId=region_info["userId"],
			password=region_info["password"],
		)
