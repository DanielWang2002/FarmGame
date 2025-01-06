import pandas as pd
import os

# 定义文件夹路径
folder_path = 'changenote'

# 获取文件夹下所有 CSV 文件
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# 初始化一个空的 DataFrame
combined_df = pd.DataFrame()

# 循环读取每个 CSV 文件并合并
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    combined_df = pd.concat([combined_df, df], ignore_index=True)
# 重置 Instance ID 列
combined_df['Instance ID'] = range(1, len(combined_df) + 1)
# 保存合并后的 DataFrame 到新的 CSV 文件
combined_df.to_csv('combined_changenote.csv', index=False)