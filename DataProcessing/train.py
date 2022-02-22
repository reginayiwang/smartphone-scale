import pandas as pd
from sklearn.model_selection import LeaveOneOut
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt


def evaluate(intensity, weight):
    y_true = []
    y_predict = []

    loo = LeaveOneOut()
    for train_index, test_index in loo.split(intensity):
        X_train, X_test = intensity[train_index], intensity[test_index]
        y_train, y_test = weight[train_index], weight[test_index]
        reg = LinearRegression().fit(X_train.values.reshape(-1, 1), y_train)
        y_predict.append(reg.predict(X_test.values.reshape(1, -1)))
        y_true.append(y_test)
    
    MAE = mean_absolute_error(y_true, y_predict)
    MAPE = mean_absolute_percentage_error(y_true, y_predict)
    return MAE, MAPE

items = ['All', 'Apple', 'Onion', 'Pepper', 'Tableware']
df = pd.read_csv('./data/data.csv')

# Evaluate model on all items combined and each item type individually
for item in items:
    if item == 'All':
        intensity = df['Intensity']
        weight = df['Weight (g)']
    else:
        item_df = df[df['Item'] == item]
        intensity = item_df['Intensity'].reset_index(drop=True)
        weight = item_df['Weight (g)'].reset_index(drop=True)
        # plt.title(item)
        # plt.scatter(weight, intensity)
        # plt.show()
        
    MAE, MAPE = evaluate(intensity, weight)
    print(f"{item}\n MAE: {MAE}, MAPE: {MAPE}")



