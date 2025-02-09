from tools.get_usd import get_usd_to_twd_rate

usd_to_twd_rate = get_usd_to_twd_rate()
print(f"💱 即時匯率: 1 USD = {usd_to_twd_rate:.2f} TWD")
import pandas as pd

type = input("請輸入類別 (1 for income / 2 for expenditure): ")
if type == "1":
    csv_file = "./output/income.csv"
elif type == "2":
    csv_file = "./output/expenditure.csv"

try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print("⚠️ 找不到 finance.csv，請先新增一筆資料！")
    exit()

print(df.tail(10))

print("\n📋 可選擇的項目:")
for i, row in enumerate(df.itertuples(), start=1):
    print(f"{i}. {row.date} - {row.item} - {row.amount}")

try:
    choice = int(input("\n請輸入要修改的項目編號 (輸入 0 退出): "))
    if choice == 0:
        print("❌ 取消修改")
        exit()
    selected_row = df.iloc[choice - 1]
except (ValueError, IndexError):
    print("⚠️ 輸入錯誤，請輸入正確的編號！")
    exit()

# 顯示選定的項目
print(f"\n🔹 你選擇了: {selected_row.date} - {selected_row.item} - {selected_row.amount}")

# 讓使用者選擇修改方式
while True:
    mode = input("請選擇更新方式: (1) 覆蓋金額 (2) 相加金額: ")
    if mode in ["1", "2", "q"]:
        break
    print("⚠️ 請輸入 1 或 2！")

# 讓使用者輸入新的金額
try:
    new_amount = float(input("請輸入新的金額: "))
except ValueError:
    print("⚠️ 金額必須是數字！")
    exit()

current = input("請輸入貨幣類型 (u for USD): ")
if current == "u":
    new_amount = float(new_amount * usd_to_twd_rate)

# 根據選擇進行更新
if mode == "1":
    df.loc[df.index[choice - 1], "amount"] = new_amount
    print(f"✅ {selected_row.item} 的金額已被**覆蓋**為 {new_amount}！")
elif mode == "2":
    df.loc[df.index[choice - 1], "amount"] += new_amount
    print(f"✅ {selected_row.item} 的金額已**增加** {new_amount}，新總額為 {df.loc[df.index[choice - 1], 'amount']}！")
elif mode == "q":
    print("❌ 取消修改")
    exit()

# 重新計算總計
df = df[df["date"] != "總計"]
total_amount = df["amount"].sum()
df.loc[len(df)] = ["總計", "", total_amount]
print(f"✅ 總計已更新為 {total_amount}！")

# 存回 CSV
df.to_csv(csv_file, index=False)

print(f"📁 {csv_file}已更新！")
