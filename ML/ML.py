import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 資料準備
file_path = './combined_changenote.csv'
data = pd.read_csv(file_path)

# 分離特徵與目標值
X = data.drop(columns=["Instance ID", "Final Coin"]).values
y = data["Final Coin"].values

# 分割訓練與測試集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 特徵標準化
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 定義激活函數與其導數
def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return np.where(x > 0, 1, 0)

# 定義損失函數與其導數
def mean_squared_error(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def mean_squared_error_derivative(y_true, y_pred):
    return -(2 / len(y_true)) * (y_true - y_pred)

# 初始化神經網路參數
input_size = X_train.shape[1]
hidden_size1 = 128
hidden_size2 = 64
output_size = 1

np.random.seed(42)
W1 = np.random.randn(input_size, hidden_size1) * 0.01
b1 = np.zeros((1, hidden_size1))
W2 = np.random.randn(hidden_size1, hidden_size2) * 0.01
b2 = np.zeros((1, hidden_size2))
W3 = np.random.randn(hidden_size2, output_size) * 0.01
b3 = np.zeros((1, output_size))

# 設定超參數
learning_rate = 0.001
epochs = 500

# 訓練神經網路
for epoch in range(epochs):
    # 前向傳播
    Z1 = np.dot(X_train, W1) + b1
    A1 = relu(Z1)
    Z2 = np.dot(A1, W2) + b2
    A2 = relu(Z2)
    Z3 = np.dot(A2, W3) + b3
    y_pred = Z3  # 最後一層為線性輸出

    # 計算損失
    loss = mean_squared_error(y_train, y_pred.flatten())

    # 反向傳播
    dL_dy_pred = mean_squared_error_derivative(y_train, y_pred.flatten()).reshape(-1, 1)

    dZ3 = dL_dy_pred
    dW3 = np.dot(A2.T, dZ3)
    db3 = np.sum(dZ3, axis=0, keepdims=True)

    dA2 = np.dot(dZ3, W3.T)
    dZ2 = dA2 * relu_derivative(Z2)
    dW2 = np.dot(A1.T, dZ2)
    db2 = np.sum(dZ2, axis=0, keepdims=True)

    dA1 = np.dot(dZ2, W2.T)
    dZ1 = dA1 * relu_derivative(Z1)
    dW1 = np.dot(X_train.T, dZ1)
    db1 = np.sum(dZ1, axis=0, keepdims=True)

    # 更新權重與偏置
    W3 -= learning_rate * dW3
    b3 -= learning_rate * db3
    W2 -= learning_rate * dW2
    b2 -= learning_rate * db2
    W1 -= learning_rate * dW1
    b1 -= learning_rate * db1

    # 每 50 個 epoch 輸出一次損失
    if (epoch + 1) % 50 == 0:
        print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.4f}")

# 測試模型
Z1_test = np.dot(X_test, W1) + b1
A1_test = relu(Z1_test)
Z2_test = np.dot(A1_test, W2) + b2
A2_test = relu(Z2_test)
Z3_test = np.dot(A2_test, W3) + b3

y_test_pred = Z3_test.flatten()

# 計算測試損失
test_loss = mean_squared_error(y_test, y_test_pred)
print(f"Test Loss: {test_loss:.4f}")

# 範例預測
example_input = scaler.transform(np.array([[100, 50, 20, 0, 60, 0.05, 115, 0.1, 0, 0.2]]))
Z1_example = np.dot(example_input, W1) + b1
A1_example = relu(Z1_example)
Z2_example = np.dot(A1_example, W2) + b2
A2_example = relu(Z2_example)
Z3_example = np.dot(A2_example, W3) + b3
example_output = Z3_example.flatten()[0]

print(f"Example Prediction for Input: {example_output:.2f}")