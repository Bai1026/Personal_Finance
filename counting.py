import argparse

import pandas as pd
from rich import print


def count_salary():
    csv_file = "./output/income.csv"
    df = pd.read_csv(csv_file)

    df = df[df["date"] != "總計"]

    genibuilder_salary = df[df["item"] == "Genibuilder 薪水"]
    total_salary = genibuilder_salary["amount"].sum()
    
    # also check for "Genibuilder 獎金"
    genibuilder_bonus = df[df["item"] == "Genibuilder 獎金"]
    total_bonus = genibuilder_bonus["amount"].sum()
    total_salary += total_bonus

    # also 內推獎金
    referral_bonus = df[df["item"] == "Genibuilder 內推獎金"]
    total_referral_bonus = referral_bonus["amount"].sum()
    total_salary += total_referral_bonus
    
    # 家教收入
    tutoring_income = df[df["item"].str.startswith("家教", na=False)]
    total_tutoring = tutoring_income["amount"].sum()
    total_salary += total_tutoring
    
    # print(f"💰 Genibuilder 薪水總金額: {total_salary}")
    # print(f"💰 Genibuilder 獎金總金額: {total_bonus}"
    # print all of the salary and bonus records
    print("\n📊 薪水和獎金記錄:"
          f"\n{genibuilder_salary.to_string(index=False)}"
          f"\n{genibuilder_bonus.to_string(index=False)}"
          f"\n{referral_bonus.to_string(index=False)}"
          f"\n{tutoring_income.to_string(index=False)}")
    print(f"\n💰 總金額: {total_salary}")

def count_by_category():
    csv_file = "./output/income.csv"
    df = pd.read_csv(csv_file)

    df = df[df["date"] != "總計"]

    print("請選擇類別：")
    print("1. Genibuilder開頭")
    print("2. 家教開頭")
    
    choice = input("請輸入選擇 (1 or 2): ")
    
    if choice == "1":
        category_df = df[df["item"].str.startswith("Genibuilder", na=False)]
        category_name = "Genibuilder"
    elif choice == "2":
        category_df = df[df["item"].str.startswith("家教", na=False)]
        category_name = "家教"
    else:
        print("⚠️ 無效的選擇！")
        return
    
    total_amount = category_df["amount"].sum()
    
    print(f"\n📊 {category_name} 類別記錄:")
    if category_df.empty:
        print("⚠️ 沒有符合條件的項目！")
    else:
        print(category_df.to_string(index=False))
        print(f"\n💰 {category_name} 總金額: {total_amount}")

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
    # print('請選擇要執行的動作：s=薪水, a=指定日期後金額, c=類別總數')
    # parser = argparse.ArgumentParser(description="計算薪水、指定日期後的金額或類別總數。")
    # parser.add_argument("action", choices=["s", "a", "c"], help="請選擇要執行的動作：s=薪水, a=指定日期後金額, c=類別總數")
    # args = parser.parse_args()

    action = input('請輸入要執行的動作 (s=薪水, a=指定日期後金額, c=類別總數): ').strip().lower()
    if action == "s":
        count_salary()
    elif action == "a":
        count_amount_after_date()
    elif action == "c":
        count_by_category()
