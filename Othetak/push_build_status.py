import requests
import os
from datetime import datetime


def push_build_status():
	job_name = os.getenv('JOB_NAME')  # Jenkins 환경 변수에서 잡 이름 가져오기
	if not job_name:
		job_name = "unknown_job"

	failed_time = datetime.utcnow().isoformat()
	url = f"http://localhost:9091/metrics/job/{job_name}"
	data = f"last_failed_build_time {failed_time}\n"
	response = requests.post(url, data=data)

	if response.status_code != 200:
		print("Failed to push data to Pushgateway")
	else:
		print("Data pushed to Pushgateway successfully")


if __name__ == "__main__":
	push_build_status()
