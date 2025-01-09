import requests
from datetime import datetime

# 요청할 API URL
API_URL = "https://api.othetak.com:8080/main/goods/foodSafetyRetrievalSuspensionDraft?page=1&perPage=100&prdtnm=&bsshnm="


def fetch_last_update_time(api_url):
	"""
    API 호출하여 업데이트 날짜 리스트 반환
    :param api_url: 호출할 API URL
    :return: 업데이트 날짜 리스트 (문자열 형식) 또는 None
    """
	try:
		# API 요청
		response = requests.get(api_url)

		# 상태 코드 확인
		if response.status_code == 200:
			try:
				# JSON 데이터 파싱
				data = response.json()

				# "data > contents" 값 가져오기
				contents = data.get("data", {}).get("contents", {})

				if isinstance(contents, list):  # 리스트인 경우 처리
					# 각 항목에서 "lastUpdateDateTime" 값 추출
					last_update_times = [item.get("lastUpdateDateTime") for item in contents if isinstance(item, dict)]
					if last_update_times:
						print("lastUpdateDateTime 값:", last_update_times)
						return last_update_times
					else:
						print("lastUpdateDateTime 값을 찾을 수 없습니다.")
						return None

				elif isinstance(contents, dict):  # 딕셔너리인 경우 처리
					# 딕셔너리 내에서 "lastUpdateDateTime" 확인
					if "lastUpdateDateTime" in contents:
						last_update_time = contents.get("lastUpdateDateTime")
						print("lastUpdateDateTime 값:", last_update_time)
						return [last_update_time]
					# 딕셔너리 내부 리스트("details") 처리
					elif "details" in contents and isinstance(contents["details"], list):
						last_update_times = [
							item.get("lastUpdateDateTime")
							for item in contents["details"]
							if isinstance(item, dict) and "lastUpdateDateTime" in item
						]
						print("details 내 lastUpdateDateTime 값:", last_update_times)
						return last_update_times if last_update_times else None
					else:
						print("'contents' 딕셔너리에 업데이트 정보가 없습니다.")
						return None
				else:
					print("'contents'의 예기치 않은 타입:", type(contents))
					return None
			except ValueError:
				print("응답 데이터가 JSON 형식이 아닙니다.")
				return None
		else:
			# 상태 코드가 200이 아닐 때 응답 내용을 출력
			print(f"API 호출 실패, 상태 코드: {response.status_code}, 응답 내용: {response.text}")
			return None
	except requests.exceptions.RequestException as e:
		print(f"API 요청 중 에러 발생: {e}")
		return None


def push_to_prometheus(update_time):
	"""
    Prometheus Pushgateway로 가장 최근의 업데이트 시간 (Unix Timestamp)을 전송
    :param update_time: 가장 최근 업데이트 날짜 (ISO8601 문자열)
    :return: HTTP 상태 코드 (정상: 200)
    """
	url = "http://localhost:9091/metrics/job/suspend_update"

	try:
		# 업데이트 날짜 문자열을 Unix 타임스탬프(초 단위 정수)로 변환
		dt = datetime.fromisoformat(update_time.replace("Z", "+00:00"))  # ISO8601 형식 처리
		unix_timestamp = int(dt.timestamp())  # 정수형 Unix Timestamp 값

		# Prometheus 메트릭 데이터 준비
		metric_name = "suspend_update_last_time"
		data = f"{metric_name} {unix_timestamp}\n"

		# Pushgateway로 전송
		response = requests.post(url, data=data)

		print(f"Prometheus에 전송된 데이터: {data.strip()}")
		return response.status_code
	except ValueError:
		print(f"유효하지 않은 날짜 형식: {update_time}")
		return None
	except requests.exceptions.RequestException as e:
		print(f"Prometheus 전송 중 에러 발생: {e}")
		return None


if __name__ == "__main__":
	# API 호출 및 결과 출력
	result = fetch_last_update_time(API_URL)
	if result:
		print("최종 업데이트 시간 리스트:", result)

		# 가장 최근 업데이트 시간 추출
		recent_update_time = max(result) if result else None
		if recent_update_time:
			print("가장 최근 업데이트 시간:", recent_update_time)

			# Prometheus에 전송
			status_code = push_to_prometheus(recent_update_time)
			if status_code == 200:
				print("업데이트 시간이 성공적으로 Prometheus에 전송되었습니다.")
			else:
				print(f"Prometheus 전송 실패, 상태 코드: {status_code}")
	else:
		print("최종 업데이트 정보를 가져오지 못했습니다.")
