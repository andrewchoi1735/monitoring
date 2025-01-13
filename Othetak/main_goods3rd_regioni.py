import requests
import sys
import json  # 디버깅용

api_url = "https://api.othetak.com:8080/main/goods3rd"


def push_to_prometheus(section, count):
	url = f"http://localhost:9091/metrics/job/goods_incheon/section/{section}"
	data = f"section_count {count}\n"
	response = requests.post(url, data=data)
	if response.status_code == 200:
		print(f"Section '{section}' count {count} successfully pushed to Prometheus.")
	else:
		print(f"Failed to push count for section '{section}' to Prometheus. Status code: {response.status_code}")
		sys.exit(1)


def check_api_data_count(api_url="https://api.othetak.com:8080/main/goods3rd"):
	try:
		# API 호출
		response = requests.get(api_url)
		response.raise_for_status()
		data = response.json()

		# # 디버깅용: 전체 응답 출력
		# print("Full API Response:")
		# print(json.dumps(data, indent=4))

		# 응답 검증
		if not data or "data" not in data:
			print("API responded with empty or invalid data.")
			sys.exit(1)

		# 섹션 데이터 확인 및 카운트
		sections = ["best", "highBasicSearch", "new", "recommend"]
		section_counts = {}

		for section in sections:
			count = len(data["data"].get(section, []))
			section_counts[section] = count
			print(f"Section '{section}' item count: {count}")

		# Prometheus로 전송
		for section, count in section_counts.items():
			push_to_prometheus(section, count)

		print("API is Normal.")
		return True

	except requests.exceptions.RequestException as e:
		print(f"API request error: {e}")
		sys.exit(1)
	except Exception as e:
		print(f"Unexpected error: {e}")
		sys.exit(1)


if __name__ == "__main__":
	check_api_data_count(api_url)
