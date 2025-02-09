import re
import sys
import os

# 加入上層資料夾到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nicegui import ui
import pandas as pd
from tools.get_usd import get_usd_to_twd_rate
from tools.get_stock import get_tse_stock_price, stock_dict

FILE_PATH = "../data/finance.txt"


# **讀取 DataFrame**
def read_finance_data():
    df = pd.read_csv(FILE_PATH)
    return df


df = read_finance_data()


# **更新 UI 顯示**
def refresh_table():
    data_table.rows[:] = df.to_dict("records")
    ui.notify("表格已更新！", type="positive")


# **計算總金額**
def calculate_total():
    usd_to_twd_rate = get_usd_to_twd_rate()
    if usd_to_twd_rate is None:
        usd_to_twd_rate = 31.5

    total_twd = 0
    cash_flow = 0

    for _, row in df.iterrows():
        item, amount = row["item"], row["amount"]
        print(f"🔹 {item} - {amount}")

        # **確保 amount_str 是字串**
        if isinstance(amount, (int, float)):
            amount = str(amount)  # 轉為字串
        else:
            amount = amount.strip()  # 若已是字串，去除前後空格

        # **現金流**
        if item in ["玉山", "郵局", "富邦", "國泰"]:
            cash_flow += int(amount)
            total_twd += int(amount)
            continue

        if "USD" in amount:
            match_usd = re.match(r"([\d\.]+)\s*\(USD\)", amount)
            print(match_usd)
            usd_value = float(match_usd.group(1))  # 取美金數字
            twd_amount = int(usd_value * usd_to_twd_rate)  # 美金轉台幣
            print(f"🔄 {usd_value} USD 轉換為 {twd_amount} TWD")
            total_twd += twd_amount
            continue

        # **解析台股股數**
        match_stock = re.match(r"台股\s+(.+)", item)
        if match_stock:
            stock_name = match_stock.group(1)
            stock_symbol = stock_dict.get(stock_name, None)

            if stock_symbol:
                price = get_tse_stock_price(stock_symbol, "tse" if stock_symbol != "4726" else "otc")

                if price and price.replace(".", "", 1).isdigit():  # 確保 `price` 是數字
                    try:
                        twd_value = int(float(price) * int(amount.strip()))  # 轉換計算
                        print(f"📈 {stock_name} ({stock_symbol}) {amount} 股，每股 {price} TWD，總值: {twd_value} TWD")
                        total_twd += twd_value
                    except ValueError:
                        print(f"⚠️ 無法計算 {stock_name} ({stock_symbol})，價格或股數錯誤: price={price}, amount={amount}")
                else:
                    print(f"⚠️ 無法獲取 {stock_name} ({stock_symbol}) 的有效股價，回傳: {price}")
            else:
                print(f"⚠️ 找不到 {stock_name} 對應的股票代號")
            continue

        try:
            twd_amount = int(amount)
            print(f"💰 {item}: {twd_amount} TWD")
            total_twd += twd_amount
        except ValueError:
            print(f"⚠️ 無法解析數值: {amount}")

    ui.notify(f"總金額: {total_twd} TWD\n現金流: {cash_flow} TWD", type="info")


# **修改項目**
def edit_item(row):
    with ui.dialog() as dialog, ui.card():
        ui.label(f"編輯項目: {row['item']}")
        new_amount = ui.input("輸入新金額/股數", value=str(row["amount"]))

        def save():
            df.loc[df["item"] == row["item"], "amount"] = new_amount.value
            df.to_csv(FILE_PATH, index=False)
            refresh_table()
            dialog.close()

        ui.button("儲存", on_click=save)
        ui.button("取消", on_click=dialog.close)


# **UI 設計**
ui.label("💰 財務管理系統").classes("text-2xl font-bold")
ui.button("計算總金額", on_click=calculate_total)
ui.button("重新載入", on_click=refresh_table)

# **顯示財務表格**
data_table = ui.table(
    columns=[
        {
            "name": "item",
            "label": "項目",
            "field": "item"
        },
        {
            "name": "amount",
            "label": "金額",
            "field": "amount"
        },
        {
            "name": "edit",
            "label": "編輯",
            "field": "edit"
        },  # 新增 "編輯" 欄位
    ],
    rows=[])

# from functools import partial

# def refresh_table():
#     data_table.rows.clear()  # 清空舊資料

#     for _, row in df.iterrows():
#         with ui.row():  # 確保 UI 元素不會影響 JSON
#             ui.label(row["item"]).style("width: 100px;")  # 項目名稱
#             ui.label(str(row["amount"])).style("width: 80px;")  # 金額
#             ui.button("編輯", on_click=partial(edit_item, row))  # 使用 partial 來正確傳遞 row

#     ui.notify("表格已更新！", type="positive")


# **更新 UI 顯示**
def refresh_table():
    data_table.rows.clear()  # 清空舊資料

    for _, row in df.iterrows():
        with ui.row():  # 確保 UI 元素不會影響 JSON
            ui.label(row["item"]).style("width: 100px;")  # 項目名稱
            ui.label(str(row["amount"])).style("width: 80px;")  # 金額
            ui.button("編輯", on_click=lambda r=row: edit_item(r))  # 讓按鈕不在 JSON 內

    ui.notify("表格已更新！", type="positive")


# **啟動 UI**
refresh_table()
ui.run()
