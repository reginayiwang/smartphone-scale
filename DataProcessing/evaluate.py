import warnings 
warnings.filterwarnings('ignore')

import csv
import signals 
import numpy as np
import pandas as pd
from pprint import pprint
from argparse import ArgumentParser
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from sklearn.ensemble import RandomForestRegressor

def evaluate(food,train_data,test_data,models=[]):
    results = list()
    for mod in models:
        preds = list()
        mod[1].fit(*train_data)
        preds = mod[1].predict(test_data[0])
        mae = mean_absolute_error(test_data[1],preds)
        mape = mean_absolute_percentage_error(test_data[1],preds)
        results.append({
            'CLASS':food,
            'MODEL':mod[0],
            'MAE':round(mae,4),
            'MAPE':round(100*mape,4)}) 
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
    fields = ['CLASS','MODEL','MAE','MAPE']
    results_file = open(fname,'w')
    author = csv.DictWriter(results_file,fieldnames=fields) 
    author.writeheader()
    return author

def make_og_feats(df,prune_outliers=True):
    feats,weights = list(),list() 
    mu,std = df['weight'].mean(),df['weight'].std()
    for _,row in df.iterrows():
        if prune_outliers and row['weight'] > mu + 2*std: continue 
        if prune_outliers and row['weight'] < mu - 2*std: continue
        feats.append(row['classic_intensity'])
        weights.append(row['weight'])
    return [np.array(feats),np.array(weights)]

def prep_og_data(path='data/all_data'):
    df = pd.DataFrame.from_dict(signals.parse_folder(path))
    apples = make_og_feats(df[df['class']=='Apple'])
    onions = make_og_feats(df[df['class']=='Onion'])
    pears = make_og_feats(df[df['class']=='Pear'])
    all_food = make_og_feats(df)
    return {'Apples':apples,'Onions':onions,'Pears':pears,'All Food':all_food}

def main(args):
    author = prep_results(args.output_file)
    names = ['LinReg','Lasso','Ridge','ElasticNet']
    models = [LinearRegression(),Lasso(),Ridge(),ElasticNet()]
    if args.vibroscale == False: 
        print('Using Advanced Vibroscale Method')
        train_data = prep_data(args.train_data)
        test_data = prep_data(args.test_data)
        for food in train_data.keys():
            count,minw,maxw = len(train_data[food][1]),train_data[food][1].min(),train_data[food][1].max()
            results = evaluate(food,train_data[food],test_data[food],list(zip(names,models)))
            author.writerows(results)
            if args.quiet_mode == False: 
                print(f'--> Evaluating {food}')
                print(f'Count: {count}  Min/Max: {minw}/{maxw}')
                pprint(results)
    else:
        print('Using Original Vibroscale Method')
        train_data = prep_og_data(args.train_data)
        test_data = prep_og_data(args.test_data)
        for food in train_data.keys():
            count,minw,maxw = len(train_data[food][1]),train_data[food][1].min(),train_data[food][1].max()
            results = evaluate(food,train_data[food],test_data[food],list(zip(names,models)))
            author.writerows(results)
            if args.quiet_mode == False: 
                print(f'--> Evaluating {food}')
                print(f'Count: {count}  Min/Max: {minw}/{maxw}')
                pprint(results)
    

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('--vibroscale',default=False,action='store_true')
    parser.add_argument('-q','--quiet_mode',default=False,action='store_true')
    parser.add_argument('--train_data',default='data/regina_03-29-22')
    parser.add_argument('--test_data',default='data/ram_04-01-22')
    parser.add_argument('-o','--output_file',default='regina_to_ram_results.csv')
    main(parser.parse_args())