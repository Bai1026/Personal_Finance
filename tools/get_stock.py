import requests


def get_tse_stock_price(stock_symbol, market="tse"):
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={market}_{stock_symbol}.tw"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "msgArray" in data and len(data["msgArray"]) > 0:
            price = data["msgArray"][0]["z"]  # 最新成交價
            return price
        else:
            return None
    except Exception as e:
        print(f"⚠️ 無法獲取 {market}_{stock_symbol} 的股價: {e}")
        return None


stock_dict = {"00878": "00878", "台積": "2330", "玉山金": "2884", "台達電": "2308", "緯創": "3231", "中租": "5871", "永昕": "4726"}
