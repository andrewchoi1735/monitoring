import requests

# API URL
api_url = "https://api.othetak.com:8080/v2/guest/goods/integrated-landing-record"
params = {
	"sortBasisCode":"",
	"perPage":100,
	"priceBasisDate":"2025-01-09",
	"distributionSpecialtyName":"",
	"storeName":"",
	"goodsName":"",
	"ingredientAndContent":"",
	"standards":"",
	"page":1
}


def check_api_data_count(api_url, params):
	try:
		response = requests.get(api_url, params=params)
		response.raise_for_status()
		data = response.json()
		item_count = len(data["data"]["goodsIntegrated"])
		print(f"Total number of items: {item_count}")
		push_to_prometheus(item_count)
	except requests.exceptions.RequestException as e:
		print("API request error:", e)
	except KeyError:
		print("Unexpected API response structure.")


def push_to_prometheus(count):
	url = "http://localhost:9091/metrics/job/my_job"
	data = f"count {count}\n"
	response = requests.post(url, data=data)
	return response.status_code


if __name__ == "__main__":
	check_api_data_count(api_url, params)
