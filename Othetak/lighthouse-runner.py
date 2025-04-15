import subprocess
import json
import statistics
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import platform
import shutil
import concurrent.futures
import logging
import TOKEN

# ========== 로깅 설정 ==========
logging.basicConfig(
	level=logging.WARNING,
	format='[%(asctime)s] [%(threadName)s] %(message)s',
	datefmt='%H:%M:%S'
)

# ========== 설정 ==========
Lighthouse_PATH = r"C:\Users\doyun\AppData\Roaming\npm\lighthouse.cmd"
REPEAT = 3
SLACK_CHANNEL = TOKEN.SLACK_CHANNEL
SLACK_TOKEN = TOKEN.SLACK_TOKEN

# 환경별 base URL 설정
ENV_URLS = {
	"stage":"https://stage.thetak.net",
	"qa":"https://qa.thetak.net",
	"prod":"https://othetak.com"
}

# URL 경로 목록
URL_PATHS = [
	"/",
	"/goods/info/agriculture",
	"/goods/info/industrial"
]


# ========== Slack 전송 함수 ==========
def send_slack_notification(url, summary_msg):
	client = WebClient(token=SLACK_TOKEN)
	try:
		response = client.chat_postMessage(
			channel=SLACK_CHANNEL,
			text=summary_msg,
			unfurl_links=False,
			blocks=[
				{
					"type":"header",
					"text":{
						"type":"plain_text",
						"text":"📊 Lighthouse 자동 점수 리포트",
						"emoji":True
					}
				},
				{
					"type":"section",
					"fields":[
						{
							"type":"mrkdwn",
							"text":f"*🌐 URL:*\n<{url}>"
						},
						{
							"type":"mrkdwn",
							"text":f"*🕒 측정횟수:*\n{REPEAT}회"
						}
					]
				},
				{"type":"divider"},
				{
					"type":"section",
					"text":{
						"type":"mrkdwn",
						"text":summary_msg
					}
				},
				{"type":"divider"},
				{
					"type":"section",
					"text":{
						"type":"mrkdwn",
						"text":get_lighthouse_env()
					}
				}
			]
		)
		logging.info(f"✅ [Slack 메시지 전송 완료] 종료된 url >> {url}")
	except SlackApiError as e:
		logging.error(f"❌ Slack API Error: {e.response['error']}")
	except Exception as e:
		logging.error(f"❌ Unexpected error: {e}")


# ========== 환경 정보 ==========
def get_lighthouse_env():
	node_ver = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
	lh_ver = subprocess.run([Lighthouse_PATH, "--version"], capture_output=True, text=True).stdout.strip()
	os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
	return (
		"*🧰 실행 환경 정보:*\n"
		f"• OS: `{os_info}`\n"
		f"• Node.js: `{node_ver}`\n"
		f"• Lighthouse: `{lh_ver}`\n"
	)


# ========== URL 하나 측정 함수 ==========
def measure_url(url):
	category_scores = {
		"performance":[],
		"accessibility":[],
		"best-practices":[],
		"seo":[]
	}

	for i in range(REPEAT):
		logging.info(f"🔁 Run #{i + 1} for {url}")
		result = subprocess.run([
			Lighthouse_PATH,
			url,
			"--output=json",
			"--quiet",
			"--chrome-flags=--headless",
			"--output-path=report.json"
		], capture_output=True, text=True)

		if result.returncode != 0:
			logging.error(f"❌ Lighthouse 실행 실패: {url} -> {result.stderr}")
			continue

		with open("report.json", "r", encoding="utf-8") as f:
			report = json.load(f)
			categories = report["categories"]

			for key in category_scores:
				score = categories.get(key, {}).get("score", None)
				if score is not None:
					score = score * 100
					category_scores[key].append(score)

	# 평균 계산 및 Slack 전송
	if any(category_scores.values()):
		message_lines = []
		for key, scores in category_scores.items():
			if scores:
				avg = round(statistics.mean(scores), 2)
				status = "🟢" if avg >= 90 else ("🟡" if avg >= 70 else "🔴")
				message_lines.append(f"*{status} {key.title()}*: `{avg}`")
			else:
				message_lines.append(f"*⚪ {key.title()}*: `점수 없음`")

		summary_message = "\n".join(message_lines)
		send_slack_notification(url, summary_message)
	else:
		logging.warning(f"⚠️ {url}의 유효한 Lighthouse 점수가 없습니다.")


# ========== 실행 ==========
if __name__ == "__main__":
	print("🎯 환경을 선택하세요 [stage / qa / prod]: ", end="")
	env = input().strip().lower()

	if env not in ENV_URLS:
		print(f"❌ 지원하지 않는 환경입니다: {env}")
		exit(1)

	base_url = ENV_URLS[env]
	full_urls = [base_url + path for path in URL_PATHS]

	with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
		executor.map(measure_url, full_urls)
