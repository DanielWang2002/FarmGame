import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    """
    這支程式會:
    1. 自動掃描 log/ 資料夾裡的所有 CSV 檔案
    2. 逐一讀取, 並給予每個檔案一個 GameID(連號)
    3. 合併所有讀取的資料成一個大 DataFrame
    4. 把 EntryType='STATE' 與 EntryType='ACTION' 分開分析
    5. 做簡單的統計與視覺化示範
    """

    # ========== [步驟 1] 找到所有CSV檔 ==========

    csv_files = glob.glob("./log/*.csv")  # 尋找 log 資料夾下所有 .csv 檔
    if not csv_files:
        print("【錯誤】在 log/ 資料夾找不到任何 CSV 檔案，請確認檔名與路徑。")
        return

    print(f"在 log/ 中共找到 {len(csv_files)} 個 CSV 檔案。")
    for f in csv_files:
        print(" -", f)

    # ========== [步驟 2] 逐檔讀取 & 合併，並加上 GameID = i ==========

    all_data = []
    for i, file_path in enumerate(csv_files, start=1):
        # i 從 1 開始遞增，代表第 i 個檔案
        df = pd.read_csv(file_path)

        # 給予 GameID 欄位 (第 i 個檔案)
        df["GameID"] = i

        # 也可以把檔案名稱放入 DataFrame，用來做後續追蹤
        df["FileName"] = os.path.basename(file_path)

        # 合併到 all_data 清單
        all_data.append(df)

    # 將所有 DataFrame 串起來
    merged_df = pd.concat(all_data, ignore_index=True)

    # 檢查一下合併後的資料
    print("\n合併後的資料共有", len(merged_df), "筆紀錄。")
    print("前五筆資料預覽：")
    print(merged_df.head())

    # ========== [步驟 3] 分離 STATE / ACTION ==========

    # (1) 狀態資料
    state_df = merged_df[merged_df["EntryType"] == "STATE"].copy()
    # (2) 行為資料
    action_df = merged_df[merged_df["EntryType"] == "ACTION"].copy()

    print("\n[資訊] 狀態資料共有", len(state_df), "筆。")
    print("[資訊] 行為資料共有", len(action_df), "筆。")

    # ========== [步驟 4] 做簡單的分析 (STATE) ==========

    # (A) 每個 GameID、每秒 (Time (s))，看看最大或平均的金幣
    #     假設同一秒 Coins 不同格子可能一樣, 這裡取最大值就好
    if "Coins" in state_df.columns:
        state_summary = state_df.groupby(["GameID","Time (s)"], as_index=False).agg({
            "Coins": "max"
        })
        print("\n[STATE] 每個 GameID x Time 的金幣概覽（前10筆）:")
        print(state_summary.head(10))

        # 示範: 觀察「最後一秒」金幣(最終金幣)
        max_time_df = state_summary.groupby("GameID", as_index=False)["Time (s)"].max()
        max_time_df.rename(columns={"Time (s)":"MaxTime"}, inplace=True)
        merged_state = pd.merge(state_summary, max_time_df, on="GameID", how="left")
        final_coins_df = merged_state[ merged_state["Time (s)"] == merged_state["MaxTime"] ].copy()
        final_coins_df.rename(columns={"Coins":"FinalCoins"}, inplace=True)

        print("\n[STATE] 最終金幣 (每個遊戲):")
        print(final_coins_df[["GameID","MaxTime","FinalCoins"]])

        # (B) 簡單地把某個GameID的Coins隨時間變化畫出來
        #     這邊只示範 GameID=1
        game1_data = state_summary[state_summary["GameID"]==1].copy()
        if not game1_data.empty:
            plt.figure(figsize=(8,5))
            plt.plot(game1_data["Time (s)"], game1_data["Coins"], marker='o', color='blue')
            plt.title("GameID=1: Coins over Time")
            plt.xlabel("Time (s)")
            plt.ylabel("Coins")
            plt.grid(True)
            plt.show()
        else:
            print("[STATE] 在 GameID=1 中沒有狀態資料，無法繪圖。")
    else:
        print("\n[STATE] CSV 資料中沒有 'Coins' 欄位，無法做金幣分析。")
    
    # ========== [步驟 5] 繪製最終金幣分佈 ==========
    plt.figure(figsize=(10, 6))
    sns.histplot(data=final_coins_df, x="FinalCoins", bins=10, kde=True)
    plt.title("Distribution of Final Coins across all Games")
    plt.xlabel("Final Coins")
    plt.ylabel("Number of Games")
    plt.grid(True)
    plt.show()
    # ========== [步驟 6] 檢查與行為的關聯 ==========
    if "Action" in action_df.columns:
        action_count = action_df.groupby(["GameID", "Action"]).size().reset_index(name="Count")
        action_analysis = pd.merge(final_coins_df, action_count, on="GameID", how="left")

        # 繪製行為次數與最終金幣的關聯圖
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=action_analysis, x="Count", y="FinalCoins", hue="Action")
        plt.title("Action Count vs. Final Coins")
        plt.xlabel("Action Count")
        plt.ylabel("Final Coins")
        plt.legend(title="Action Type")
        plt.grid(True)
        plt.show()
    # ========== [步驟 5] 做簡單的分析 (ACTION) ==========

    # 觀察各個行為類型(Action)，以及它們在每個遊戲(GameID)發生的次數
    if "Action" in action_df.columns:
        action_count = action_df.groupby(["GameID","Action"]).size().reset_index(name="Count")
        print("\n[ACTION] 各遊戲中不同行為類型的次數：")
        print(action_count)

        # 如果你想把它跟「最終金幣」對比，可以 merge 到剛剛 final_coins_df
        if "FinalCoins" in final_coins_df.columns:
            # 先只留 GameID, FinalCoins
            final_coins_merge = final_coins_df[["GameID","FinalCoins"]].drop_duplicates()

            action_analysis = pd.merge(action_count, final_coins_merge, on="GameID", how="left")
            print("\n[ACTION] 加上最終金幣後：")
            print(action_analysis)

            # 可以畫散佈圖：行為次數 vs. 最終金幣 (以 Harvest 為例)
            harvest_df = action_analysis[action_analysis["Action"]=="Harvest"].copy()
            if not harvest_df.empty:
                plt.figure(figsize=(6,5))
                sns.scatterplot(data=harvest_df, x="Count", y="FinalCoins")
                plt.title("Harvest Count vs. FinalCoins (per Game)")
                plt.xlabel("Harvest Count")
                plt.ylabel("Final Coins")
                plt.grid(True)
                plt.show()
            else:
                print("[ACTION] 沒有 Harvest 資料，無法繪圖。")
        else:
            print("\n[ACTION] 無法與最終金幣對照，因為 'FinalCoins' 資料不足。")
    else:
        print("\n[ACTION] CSV 資料中沒有 'Action' 欄位，無法做行為分析。")
    # ========== [步驟 6] 分析可調參數對結果的影響 ==========

    # 假設探討 'Soil Level' 和 'Plant Level' 對 'Coins' 的影響
    if "Soil Level" in state_df.columns and "Plant Level" in state_df.columns and "Coins" in state_df.columns:
        # 繪製 Soil Level 與 Coins 的關係
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=state_df, x="Soil Level", y="Coins")
        plt.title("Soil Level vs. Coins")
        plt.xlabel("Soil Level")
        plt.ylabel("Coins")
        plt.grid(True)
        plt.show()

        # 繪製 Plant Level 與 Coins 的關係
        plt.figure(figsize=(8, 5))
        sns.boxplot(data=state_df, x="Plant Level", y="Coins")
        plt.title("Plant Level vs. Coins")
        plt.xlabel("Plant Level")
        plt.ylabel("Coins")
        plt.grid(True)
        plt.show()

        # 如果需要更詳細的統計，可以按 Soil Level 和 Plant Level 分組後計算 Coins 平均值
        grouped_df = state_df.groupby(["Soil Level", "Plant Level"], as_index=False).agg({
            "Coins": "mean"
        })
        print("\n[分析] Soil Level 和 Plant Level 對 Coins 的影響：")
        print(grouped_df)

        # 繪製多變數影響圖 (例如 Soil Level 與 Plant Level 同時影響 Coins)
        pivot_table = grouped_df.pivot(index="Soil Level", columns="Plant Level", values="Coins")
        plt.figure(figsize=(10, 6))
        sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="YlGnBu")
        plt.title("Soil Level and Plant Level vs. Coins")
        plt.xlabel("Plant Level")
        plt.ylabel("Soil Level")
        plt.show()

    else:
        print("\n[分析] 缺少 'Soil Level', 'Plant Level', 或 'Coins' 欄位，無法進行參數分析。")

    # ========== 分析結束 ==========
    print("\n程式執行完畢。若要做更深入的分析，可依照需求自行修改或擴充。")

if __name__ == "__main__":
    main()
