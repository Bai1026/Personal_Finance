import requests


def get_usd_to_twd_rate():
    url = "https://open.er-api.com/v6/latest/USD"
    try:
        response = requests.get(url, timeout=5)  # 設置超時時間，避免無限等待
        response.raise_for_status()  # 檢查是否請求成功 (HTTP 200)
        data = response.json()

        # 檢查 API 回傳格式
        if "rates" in data and "TWD" in data["rates"]:
            return data["rates"]["TWD"]
        else:
            print("⚠️ API 回應異常，找不到 TWD 匯率！")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ 無法獲取匯率: {e}")
        return None
