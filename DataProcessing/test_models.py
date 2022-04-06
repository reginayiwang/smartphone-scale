import warnings

from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error 
warnings.filterwarnings('ignore')

import csv
import time
import signals 
import numpy as np
import pandas as pd
from pprint import pprint
from argparse import ArgumentParser
from sklearn.decomposition import PCA 
from sklearn.model_selection import LeaveOneOut
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Lasso, Ridge, ElasticNet

def pca_transform(feats,n_components=5):
    return PCA(n_components).fit_transform(feats)

def get_runtimes(model,feats,weights):
    start_traintime = time.time()
    model.fit(feats,weights)
    end_traintime = time.time() - start_traintime
    start_testtime = time.time()
    _ = model.score(feats,weights)
    end_testtime = time.time() - start_testtime
    return end_traintime,end_testtime

def evaluate(food,feats,weights,models=[],use_pca=False):
    results = list()
    if use_pca:
        print('Before PCA:',feats.shape)
        feats = pca_transform(feats)
        print('After PCA:',feats.shape)
    for mod in models:
        ytrue,ypred = list(),list()
        loo = LeaveOneOut()
        for trainx,testx in loo.split(feats):
            xtrain,xtest = feats[trainx],feats[testx]
            ytrain,ytest = weights[trainx],weights[testx]
            clf = mod[1].fit(xtrain,ytrain)
            ypred.append(clf.predict(xtest))
            ytrue.append(ytest)
        mae = mean_absolute_error(ytrue,ypred)
        mape = mean_absolute_percentage_error(ytrue,ypred)
        train_time,test_time = get_runtimes(mod[1],feats,weights)
        results.append({
            'CLASS':food,
            'MODEL':mod[0],
            'MAE':round(mae,4),
            'MAPE':round(100*mape,4),
            'TRAIN TIME':round(train_time,6),
            'TEST TIME':round(test_time,6)}) 
    return results

def make_feats(df,prune_outliers=True):
    feats,weights = list(),list() 
    mu,std = df['weight'].mean(),df['weight'].std()
    for _,row in df.iterrows():
        if prune_outliers and row['weight'] > mu + 2*std: continue 
        if prune_outliers and row['weight'] < mu - 2*std: continue
        cin = row['classic_intensity']
        fin = row['filtered_intensity']
        lips = row['left_ips']
        rips = row['right_ips']
        pmag = row['peak_magnitude']
        pfre = row['peak_frequency']
        feats.append(np.concatenate((fin,lips,rips,pmag),axis=0))
        weights.append(row['weight'])
    return [np.array(feats),np.array(weights)]

def prep_data(path='data/all_data'):
    df = pd.DataFrame.from_dict(signals.parse_folder(path))
    apples = make_feats(df[df['class']=='Apple'])
    onions = make_feats(df[df['class']=='Onion'])
    pears = make_feats(df[df['class']=='Pear'])
    all_food = make_feats(df)
    return {'Apples':apples,'Onions':onions,'Pears':pears,'All Food':all_food}

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

def prep_results(fname='/results/all_data_results.csv'):
    fields = ['CLASS','MODEL','MAE','MAPE','TRAIN TIME','TEST TIME']
    results_file = open(fname,'w')
    author = csv.DictWriter(results_file,fieldnames=fields) 
    author.writeheader()
    return author

def main(args):
    data = prep_data(args.input_dir) 
    author = prep_results(args.output_file)
    names = ['Linear Regression','Lasso','Ridge','Elastic Net','Random Forest']
    models = [
        LinearRegression(),
        Lasso(alpha=1.0,selection='cyclic'),
        Ridge(alpha=1.0,solver='saga'),
        ElasticNet(alpha=1.0,l1_ratio=0.9,selection='cyclic'),
        RandomForestRegressor(
            ccp_alpha=0.2,
            criterion='absolute_error',
            n_estimators=10,
            max_depth=5)]
    for k,v in data.items():
        count,minw,maxw = len(v[1]),v[1].min(),v[1].max()
        results = evaluate(k,v[0],v[1],list(zip(names,models)),args.pca)
        author.writerows(results)
        if args.verbose: 
            print(f'\n--> Evaluating {k}')
            print(f'Count: {count}  Min/Max: {minw}/{maxw}')
            pprint(results)
    og_data = prep_og_data(args.input_dir)
    for k,v in og_data.items():
        count,minw,maxw = len(v[1]),v[1].min(),v[1].max()
        results = evaluate(k,v[0],v[1],list(zip(names,models)),args.pca)
        if args.verbose: 
            print(f'\n--> (OG) Evaluating {k}')
            print(f'Count: {count}  Min/Max: {minw}/{maxw}')
            pprint(results)

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('-v','--verbose',default=False,action='store_true')
    parser.add_argument('-i','--input_dir',default='data/all_data')
    parser.add_argument('-o','--output_file',default='results/all_data_results.csv')
    parser.add_argument('--pca',default=False,action='store_true')
    main(parser.parse_args())