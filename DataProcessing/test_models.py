import warnings 
warnings.filterwarnings('ignore')

import signals 
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV,cross_validate

def evaluate_lr(feats,weights):
    mod = LinearRegression()
    cv_score = cross_validate(mod,feats,weights,
        scoring=['neg_mean_absolute_error','neg_mean_absolute_percentage_error'])
    mae = cv_score['test_neg_mean_absolute_error'].mean()
    mape = cv_score['test_neg_mean_absolute_percentage_error'].mean()
    return mae,mape 

def evaluate_lasso(feats,weights):
    mod = Lasso()
    cv_score = cross_validate(mod,feats,weights,
        scoring=['neg_mean_absolute_error','neg_mean_absolute_percentage_error'])
    mae = cv_score['test_neg_mean_absolute_error'].mean()
    mape = cv_score['test_neg_mean_absolute_percentage_error'].mean()
    return mae,mape 

def evaluate_rf(feats,weights):
    params = {
        'n_estimators' : range(5,500),
        'max_depth' : list(range(1,20)) + [None],
        'min_samples_split' : [2,3,4,5,6,10],
        'min_samples_leaf': [1,2,3,4,5,6,10]}

    cv = RandomizedSearchCV(
        estimator=RandomForestRegressor(),
        n_iter=100,
        param_distributions=params,
        scoring='neg_mean_absolute_error',
        verbose=0,
        n_jobs=32).fit(feats,weights)

    mod = RandomForestRegressor(**cv.best_params_)
    cv_score = cross_validate(mod,feats,weights,
        scoring=['neg_mean_absolute_error','neg_mean_absolute_percentage_error'])
    mae = cv_score['test_neg_mean_absolute_error'].mean()
    mape = cv_score['test_neg_mean_absolute_percentage_error'].mean()
    return mae,mape 

def make_feats(df):
    feats,weights = [],[] 
    for _,row in df.iterrows():
        cin = row['classic_intensity']
        fin = row['filtered_intensity']
        lips = row['left_ips']
        rips = row['right_ips']
        pfre = row['peak_frequency']
        pmag = row['peak_magnitude']
        feats.append(np.concatenate((cin,fin,lips,rips,pfre,pmag),axis=0))
        weights.append(row['weight'])
    return [np.array(feats),np.array(weights)]

def prep_data(path='DataProcessing/data/regina_03-29-22'):
    df = pd.DataFrame.from_dict(signals.parse_folder(path))
    apples = make_feats(df[df['class']=='Apple'])
    onions = make_feats(df[df['class']=='Onion'])
    pears = make_feats(df[df['class']=='Pear'])
    all_food = make_feats(df)
    return {'Apples':apples,'Onions':onions,'Pears':pears,'All Food':all_food}

def main():
    data = prep_data() 
    for k,v in data.items():
        print(f'--> Evaluating {k}')
        count,minw,maxw = len(v[1]),v[1].min(),v[1].max()
        print(f'Count: {count}  Min/Max: {minw}/{maxw}')
        
        lr_mae,lr_mape = evaluate_lr(*v)
        print(f'(Linear Regression)  MAE: {abs(round(lr_mae,4)):.4f}',end='  ')
        print(f'MAPE: {abs(round(lr_mape,4)*100):2.2f}')
        
        lasso_mae,lasso_mape = evaluate_lasso(*v)
        print(f'(Lasso)  MAE: {abs(round(lasso_mae,4)):.4f}',end='  ')
        print(f'MAPE: {abs(round(lasso_mape,4)*100):2.2f}')
        
        rf_mae,rf_mape = evaluate_rf(*v)
        print(f'(Random Forest)  MAE: {abs(round(rf_mae,4)):.4f}',end='  ')
        print(f'MAPE: {abs(round(rf_mape,4)*100):2.2f}\n')

if __name__=='__main__':
    main()