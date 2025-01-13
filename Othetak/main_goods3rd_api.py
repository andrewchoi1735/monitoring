import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
import sys

# API URL
api_url = "https://api.othetak.com:8080/main/goods3rd"
pushgateway_url = "http://<pushgateway-host>:9091"  # PushGateway 주소


def check_api_data_count(api_url):
	try:
		# 1. API 호출
		response = requests.get(api_url)
		response.raise_for_status()
		data = response.json()

		if not isinstance(data, dict):  # 응답 데이터가 dictionary인지 확인
			print("Unexpected data type. Expected a dictionary.")
			raise ValueError(f"Invalid API response structure: {type(data)}")

		# 2. 각 섹션의 아이템 개수 계산
		sections = ["best", "highBasicSearch", "new", "recommend"]
		section_counts = {}

		for section in sections:
			section_counts[section] = len(data.get(section, []))  # 키가 없으면 빈 리스트로 처리
			print(f"Section '{section}' item count: {section_counts[section]}")

		# 3. Prometheus로 데이터 전송
		# PushGateway 연결 설정
		registry = CollectorRegistry()
		for section, count in section_counts.items():
			gauge = Gauge(f"api_items_count_{section}", f"Number of items in section {section}", registry=registry)
			gauge.set(count)

		push_to_gateway(pushgateway_url, job="api_data_count_job", registry=registry)
		print("Item counts have been successfully pushed to PushGateway.")

		# 4. 빌드 성공 처리
		print("API is Normal.")
		return True

	except requests.exceptions.RequestException as e:
		print(f"API request error: {e}")
		sys.exit(1)  # 빌드 실패로 처리
	except ValueError as e:
		print(f"ValueError: {e}")
		sys.exit(1)  # 빌드 실패로 처리
	except Exception as e:
		print(f"Unexpected error: {e}")
		sys.exit(1)  # 빌드 실패로 처리


if __name__ == "__main__":
	check_api_data_count(api_url)
