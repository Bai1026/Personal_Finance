import argparse
import re
import pandas as pd
from tools.get_usd import get_usd_to_twd_rate
from tools.get_stock import get_tse_stock_price, stock_dict


# **讀取 finance.txt 並轉成 DataFrame**
def read_finance_data(FINE_PATH):
    with open(FINE_PATH, 'r') as file:
        lines = file.readlines()

    data = []
    for line in lines:
        place, amount = line.strip().split(',')
        data.append([place, amount])

    return pd.DataFrame(data[1:], columns=["item", "amount"])


# **修改股票數量 或 一般項目**
def edit_item(FINE_PATH):
    df = read_finance_data(FINE_PATH)

    # **篩選 "台股" 和 "非台股" 項目**
    stock_df = df[df["item"].str.startswith("台股")].reset_index()
    non_stock_df = df[~df["item"].str.startswith("台股")].reset_index()

    print("\n🔹 你想修改哪種類型的項目？")
    print("1. 台股股數")
    print("2. 其他一般項目")

    option = input("請輸入選項 (1/2): ")

    if option == "1":
        target_df = stock_df
        item_type = "台股"
    elif option == "2":
        target_df = non_stock_df
        item_type = "一般項目"
    else:
        print("⚠️ 無效選擇，請輸入 1 或 2")
        return

    # **列出可修改的項目**
    print(f"\n📊 可修改的 {item_type}：")
    for i, row in target_df.iterrows():
        print(f"{i + 1}. {row['item']} - {row['amount']}")

    # **使用者輸入選擇的項目**
    try:
        choice = int(input("\n請輸入要修改的項目編號 (輸入 0 取消): "))
        if choice == 0:
            print("❌ 取消修改")
            return
        selected_item = target_df.loc[choice - 1, "item"]
    except (ValueError, IndexError):
        print("⚠️ 輸入錯誤，請輸入正確的編號！")
        return

    # **選擇要修改的內容**
    print("\n🔹 你想修改什麼？")
    if item_type == "台股":
        print("1. 修改股數")
        print("2. 修改名稱")
    else:
        print("1. 修改金額")
        print("2. 修改名稱")
        print("3. 兩者皆修改")

    edit_option = input("請輸入選項: ")

    if edit_option == "1":  # 修改股數或名稱
        if item_type == "台股":
            new_amount = input(f"🔄 請輸入新的股數 (舊: {df.loc[df['item'] == selected_item, 'amount'].values[0]}): ").strip()
            df.loc[df["item"] == selected_item, "amount"] = new_amount
        else:
            new_amount = input(f"🔄 請輸入新的金額 (舊: {df.loc[df['item'] == selected_item, 'amount'].values[0]}): ").strip()
            df.loc[df["item"] == selected_item, "amount"] = new_amount

    elif edit_option == "2":
        if item_type == "台股":
            new_name = input(f"🔄 請輸入新的名稱 (舊: {selected_item}): ").strip()
            df.loc[df["item"] == selected_item, "item"] = new_name
        else:
            new_item = input(f"🔄 請輸入新的名稱 (舊: {selected_item}): ").strip()
            df.loc[df["item"] == selected_item, "item"] = new_item

    elif edit_option == "3" and item_type == "一般項目":
        new_item = input(f"🔄 請輸入新的名稱 (舊: {selected_item}): ").strip()
        new_amount = input(f"🔄 請輸入新的金額 (舊: {df.loc[df['item'] == selected_item, 'amount'].values[0]}): ").strip()
        df.loc[df["item"] == selected_item, "item"] = new_item
        df.loc[df["item"] == selected_item, "amount"] = new_amount

    else:
        print("⚠️ 無效選擇，請輸入 1 / 2 / 3")
        return

    # **存回 CSV**
    df.to_csv(FINE_PATH, index=False, encoding="utf-8-sig")

    print("\n✅ 更新後的數據：")
    print(df)
    print(f"\n✅ 已將更新後的數據存入 {FINE_PATH}！")


# **計算總金額**
def calculate_total(FINE_PATH):
    df = read_finance_data(FINE_PATH)
    usd_to_twd_rate = get_usd_to_twd_rate()

    if usd_to_twd_rate is None:
        print("❌ 取得匯率失敗，使用預設匯率 31.5")
        usd_to_twd_rate = 31.5  # set default rate

    print(f"\n💱 即時匯率: 1 USD = {usd_to_twd_rate:.2f} TWD\n")

    total_twd = 0
    cash_flow = 0

    def convert_amount(item, amount_str):
        nonlocal total_twd
        nonlocal cash_flow

        # **確保 amount_str 是字串**
        if isinstance(amount_str, (int, float)):
            amount_str = str(amount_str)  # 轉為字串
        else:
            amount_str = amount_str.strip()  # 若已是字串，去除前後空格

        if item in ["玉山", "郵局", "富邦", "國泰"]:
            try:
                cash_amount = int(amount_str)
                cash_flow += cash_amount  # **累加現金流**
                print(f"💰 {item}: {cash_amount} TWD")
                total_twd += cash_amount
            except ValueError:
                print(f"⚠️ 無法解析數值: {amount_str}")
            return

        # **解析 純美金** (ex: "1332.03 (USD)")
        match_usd = re.match(r"([\d\.]+)\s*\(USD\)", amount_str)

        if match_usd:
            usd_value = float(match_usd.group(1))  # 取美金數字
            twd_amount = int(usd_value * usd_to_twd_rate)  # 美金轉台幣
            print(f"🔄 {usd_value} USD 轉換為 {twd_amount} TWD")
            total_twd += twd_amount
            return

        # **解析 台股 (ex: "台股 00878, 2500")**
        match_stock = re.match(r"台股\s+(.+)", item)

        if match_stock:
            stock_name = match_stock.group(1)  # 提取股票名稱
            try:
                shares = int(amount_str)  # 確保股數是 `int`
            except ValueError:
                print(f"⚠️ 無法解析股數: {amount_str}")
                return

            if stock_name in stock_dict:
                stock_symbol = stock_dict[stock_name]
                market = "tse" if stock_symbol != "4726" else "otc"

                stock_price = get_tse_stock_price(stock_symbol, market)

                if stock_price:
                    try:
                        stock_price = re.findall(r"[-+]?\d*\.\d+|\d+", stock_price)  # 取出數字
                        if stock_price:
                            stock_price = float(stock_price[0])  # 只取第一個正確數字
                        else:
                            raise ValueError("⚠️ 無法解析股價")

                        twd_value = int(stock_price * shares)  # 計算總價值
                        print(f"📈 {stock_name} ({stock_symbol}) {shares} 股，每股 {stock_price} TWD，總值: {twd_value} TWD")
                        total_twd += twd_value
                        return
                    except ValueError:
                        print(f"⚠️ 股價格式錯誤: {stock_price}")
                        return

            print(f"⚠️ 無法獲取 {stock_name} ({stock_symbol}) 的股價")
            return

        # **純台幣**
        try:
            twd_amount = int(amount_str)
            print(f"💰 {item}: {twd_amount} TWD")
            total_twd += twd_amount
        except ValueError:
            print(f"⚠️ 無法解析數值: {amount_str}")

    # **遍歷 DataFrame 並 `print` 出來**
    for _, row in df.iterrows():
        convert_amount(row["item"], row["amount"])

    # **最終總金額**
    print(f"\n💰 總金額 (包含 USD & 台股換算): {total_twd} TWD")
    print(f"🏦 現金流 (玉山、郵局、富邦、國泰): {cash_flow} TWD")


# **解析命令行參數**
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="財務數據管理工具")
    parser.add_argument("-m", "--mode", choices=["e", "t"], required=True, help="選擇功能模式：edit（修改股票數量），calculate（計算總金額）")

    FILE_PATH = "./data/finance.txt"
    args = parser.parse_args()

    # edit mode
    if args.mode == "e":
        edit_item(FILE_PATH)
    # total mode
    elif args.mode == "t":
        calculate_total(FILE_PATH)
