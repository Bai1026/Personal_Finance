import argparse
import pandas as pd


def count_salary():
    csv_file = "./output/income.csv"
    df = pd.read_csv(csv_file)

    df = df[df["date"] != "總計"]

    genibuilder_salary = df[df["item"] == "Genibuilder 薪水"]
    total_salary = genibuilder_salary["amount"].sum()

    print(f"💰 Genibuilder 薪水總金額: {total_salary}")


def count_amount_after_date():
    type = input("請輸入類別 (1 for income / 2 for expenditure): ")
    if type == "1":
        csv_file = "./output/income.csv"
    elif type == "2":
        csv_file = "./output/expenditure.csv"

    df = pd.read_csv(csv_file)

    df = df[df["date"] != "總計"]

    # 轉換日期格式，方便比較
    df["date"] = pd.to_datetime(df["date"], format="%Y/%m/%d")

    # 使用者輸入時間點
    raw_date = input("請輸入日期 (格式: YYYYMMDD，例如 20250120，輸入 q 退出): ")

    try:
        user_date = f"{raw_date[:4]}/{int(raw_date[4:6])}/{int(raw_date[6:])}"
    except (ValueError, IndexError):
        print("⚠️ 格式錯誤，請輸入正確的 YYYYMMDD！")

    # 過濾時間點之後的資料
    df_after_date = df[df["date"] >= user_date]

    # 計算總金額
    total_amount_after = df_after_date["amount"].sum()

    print(f"📅 {user_date} 之後的總金額: {total_amount_after}")
    print()

    if df_after_date.empty:
        print("⚠️ 沒有符合條件的項目！")
    else:
        print(df_after_date.to_string(index=False))  # 顯示所有符合條件的資料
        print(f"\n💰 總金額: {total_amount_after}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calculate salary and amount after a specific date.")
    parser.add_argument("-a", "--action", choices=["salary", "amount"], help="Choose the action to perform.")
    args = parser.parse_args()

    if args.action == "salary":
        count_salary()
    elif args.action == "amount":
        count_amount_after_date()
