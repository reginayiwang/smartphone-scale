import warnings 
warnings.filterwarnings('ignore')

import csv
import time
import signals 
import numpy as np
import pandas as pd
from pprint import pprint
from argparse import ArgumentParser
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate

def get_runtimes(model,feats,weights):
    start_traintime = time.time()
    model.fit(feats,weights)
    end_traintime = time.time() - start_traintime
    start_testtime = time.time()
    _ = model.score(feats,weights)
    end_testtime = time.time() - start_testtime
    return end_traintime,end_testtime

def evaluate(food,feats,weights,models=[]):
    results = list()
    for mod in models:
        cv_score = cross_validate(mod[1],feats,weights,cv=3,
            scoring=['neg_mean_absolute_error','neg_mean_absolute_percentage_error'])
        mae = cv_score['test_neg_mean_absolute_error'].mean()
        mape = cv_score['test_neg_mean_absolute_percentage_error'].mean()
        train_time,test_time = get_runtimes(mod[1],feats,weights)
        results.append({
            'CLASS':food,
            'MODEL':mod[0],
            'MAE':round(-mae,4),
            'MAPE':round(-100*mape,4),
            'TRAIN TIME':round(train_time,6),
            'TEST TIME':round(test_time,6)}) 
    return results

def make_feats(df):
    feats,weights = list(),list() 
    for _,row in df.iterrows():
        cin = row['classic_intensity']
        fin = row['filtered_intensity']
        lips = row['left_ips']
        rips = row['right_ips']
        pmag = row['peak_magnitude']
        pfre = row['peak_frequency']
        feats.append(np.concatenate((cin,fin,lips,rips,pmag,pfre),axis=0))
        weights.append(row['weight'])
    return [np.array(feats),np.array(weights)]

def prep_data(path='data/regina_03-29-22'):
    df = pd.DataFrame.from_dict(signals.parse_folder(path))
    apples = make_feats(df[df['class']=='Apple'])
    onions = make_feats(df[df['class']=='Onion'])
    pears = make_feats(df[df['class']=='Pear'])
    all_food = make_feats(df)
    return {'Apples':apples,'Onions':onions,'Pears':pears,'All Food':all_food}

def prep_results(fname='results.csv'):
    fields = ['CLASS','MODEL','MAE','MAPE','TRAIN TIME','TEST TIME']
    results_file = open(fname,'w')
    author = csv.DictWriter(results_file,fieldnames=fields) 
    author.writeheader()
    return author

def main(args):
    data = prep_data(args.input_dir) 
    author = prep_results(args.output_file)
    names = ['Linear Regression','Lasso','Ridge','Random Forest']
    models = [LinearRegression(),Lasso(),Ridge(),RandomForestRegressor()]
    for k,v in data.items():
        count,minw,maxw = len(v[1]),v[1].min(),v[1].max()
        results = evaluate(k,v[0],v[1],list(zip(names,models)))
        author.writerows(results)
        if args.verbose: 
            print(f'--> Evaluating {k}')
            print(f'Count: {count}  Min/Max: {minw}/{maxw}')
            pprint(results)

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('-v','--verbose',default=False,action='store_true')
    parser.add_argument('-i','--input_dir',default='data/regina_03-29-22')
    parser.add_argument('-o','--output_file',default='results.csv')
    main(parser.parse_args())