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

df = pd.read_csv('./data/data.csv')

# Evaluate model on all items combined and each item type individually
items = list(pd.unique(df['Item']))
items.append('All')

for item in items:
    if item == 'All':
        count = len(df)
        min_weight, max_weight = df['Weight (g)'].min(), df['Weight (g)'].max()
        intensity = df['Intensity']
        weight = df['Weight (g)']
    else:
        item_df = df[df['Item'] == item]
        count = len(item_df)
        min_weight, max_weight = item_df['Weight (g)'].min(), item_df['Weight (g)'].max()
        intensity = item_df['Intensity'].reset_index(drop=True)
        weight = item_df['Weight (g)'].reset_index(drop=True)

        # plt.title(item)
        # plt.scatter(weight, intensity)
        # plt.show()
        
    MAE, MAPE = evaluate(intensity, weight)
    print(f"{item} (n={count})\nMin/Max:  {min_weight}/{max_weight} \nMAE: {round(MAE, 1)}, MAPE: {round(MAPE, 3) * 100}\n")



