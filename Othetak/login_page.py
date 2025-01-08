import requests

URL = "https://othetak.com/auth/signIn"  # 모니터링할 웹페이지 URL


def check_website_status(url):
	try:
		response = requests.get(url)
		if response.status_code == 200:
			print("웹페이지가 정상적으로 작동하고 있습니다.")
		else:
			print("웹페이지에 문제가 있습니다. 상태 코드:", response.status_code)
	except requests.exceptions.RequestException as e:
		print("웹페이지에 문제가 있습니다. 에러 메시지:", e)


if __name__ == "__main__":
	check_website_status(URL)
