import requests
import sys

api_url = "https://api.othetak.com:8080/guest/bigBanner"


def check_api_status(api_url):
	"""
    API 상태를 확인하고 Jenkins 빌드 상태로 결정
    """
	try:
		# API 호출
		response = requests.get(api_url)
		response.raise_for_status()  # 응답이 200이 아니면 예외 발생
		print(f"API responded with status {response.status_code}: Success.")
		sys.exit(0)  # 정상 상태 (빌드 성공)

	except requests.exceptions.RequestException as e:
		# 예외 발생 시 오류 출력 및 빌드 실패
		print(f"API request failed: {e}")
		sys.exit(1)  # 비정상 상태 (빌드 실패)


if __name__ == "__main__":
	check_api_status(api_url)
