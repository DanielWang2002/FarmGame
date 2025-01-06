import os
import pandas as pd
import matplotlib.pyplot as plt

# Define the folder path
folder_path = './changenote'

# Define file names
file_names = ['initial_amount_100.csv', 'initial_amount_150.csv', 'initial_amount_200.csv', 'initial_amount_250.csv', 'initial_amount_300.csv']

# Load the CSV files
data_100 = pd.read_csv(os.path.join(folder_path, file_names[0]))
data_150 = pd.read_csv(os.path.join(folder_path, file_names[1]))
data_200 = pd.read_csv(os.path.join(folder_path, file_names[2]))
data_250 = pd.read_csv(os.path.join(folder_path, file_names[3]))
data_300 = pd.read_csv(os.path.join(folder_path, file_names[4]))

# Extract relevant data for visualization
upgrade_costs = [100,150,200,250,300]
final_coins_100 = data_100['Final Coin'].mean()
final_coins_150 = data_150['Final Coin'].mean()
final_coins_200 = data_200['Final Coin'].mean()
final_coins_250 = data_250['Final Coin'].mean()
final_coins_300 = data_300['Final Coin'].mean()

# Prepare data for visualization
final_coins_means = [final_coins_100, final_coins_150, final_coins_200, final_coins_250, final_coins_300]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(upgrade_costs, final_coins_means, marker='o', linestyle='-', linewidth=2)
plt.title('Effect of DIRT_Normal_upgrade_cost on Final Coins', fontsize=14)
plt.xlabel('DIRT_Normal_upgrade_cost', fontsize=12)
plt.ylabel('Average Final Coins', fontsize=12)
plt.grid()
plt.xticks(upgrade_costs)
plt.show()
