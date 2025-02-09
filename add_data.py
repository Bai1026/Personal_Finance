from tools.get_usd import get_usd_to_twd_rate

import pandas as pd

genre = input("請輸入類別 (1 for income / 2 for expenditure): ")
if genre == "1":
    csv_file = "./output/income.csv"
elif genre == "2":
    csv_file = "./output/expenditure.csv"

try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    df = pd.DataFrame(columns=["date", "item", "amount"])

print(df.tail(10))

usd_to_twd_rate = get_usd_to_twd_rate()
print(usd_to_twd_rate)

while True:
    raw_date = input("請輸入日期 (格式: YYYYMMDD，例如 20250120，輸入 q 退出): ")
    if raw_date.lower() == 'q':
        break

    try:
        formatted_date = f"{raw_date[:4]}/{int(raw_date[4:6])}/{int(raw_date[6:])}"
    except (ValueError, IndexError):
        print("⚠️ 格式錯誤，請輸入正確的 YYYYMMDD！")
        continue

    item = input("請輸入項目名稱: (if salary of genibuilder, please enter 1; if bonus, enter 2)")
    if item == "1":
        item = "Genibuilder 薪水"
    elif item == "2":
        item = "Genibuilder 獎金"

    amount = float(input("請輸入金額: "))

    try:
        amount = int(amount)
    except ValueError:
        print("⚠️ 金額必須是數字！")
        continue

    currency = input("enter u for USD")
    if currency == "u":
        amount = float(amount * usd_to_twd_rate)

    new_data = pd.DataFrame([[formatted_date, item, amount]], columns=["date", "item", "amount"])
    df = pd.concat([df[df["date"] != "總計"], new_data])

    df["date"] = pd.to_datetime(df["date"], errors='coerce')
    df = df.sort_values(by="date")

    df["date"] = df["date"].dt.strftime("%Y/%m/%d")

    total_amount = df["amount"].sum()
    df.loc[len(df)] = ["總計", "", total_amount]
    if genre == "1":
        print(f"總收入: {total_amount}", end='\n')
    elif genre == "2":
        print(f"總支出: {total_amount}", end='\n')

    df.to_csv(csv_file, index=False)

    print(f"✅ 已新增 {formatted_date} - {item} - {amount} 到 {csv_file}！")
