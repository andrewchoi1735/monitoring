import requests

URL = "http://provider.othetak.com"  # 모니터링할 웹페이지 URL


def check_website_status(url):
	try:
		response = requests.get(url)
		if response.status_code == 200:
			print("웹페이지가 정상적으로 작동하고 있습니다.")
			status = 1  # 정상 상태
		else:
			print("웹페이지에 문제가 있습니다. 상태 코드:", response.status_code)
			status = 0  # 문제 발생 상태
	except requests.exceptions.RequestException as e:
		print("웹페이지에 문제가 있습니다. 에러 메시지:", e)
		status = 0  # 문제 발생 상태

	push_to_prometheus(status)


def push_to_prometheus(status):
	url = "http://localhost:9091/metrics/job/oseller_status"
	data = f"oseller_status {status}\n"
	response = requests.post(url, data=data)
	return response.status_code


if __name__ == "__main__":
	check_website_status(URL)
