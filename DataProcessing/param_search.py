import warnings 
warnings.filterwarnings('ignore')

import signals 
import numpy as np
import pandas as pd
from pprint import pprint
from argparse import ArgumentParser
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Lasso, Ridge, ElasticNet
from sklearn.model_selection import GridSearchCV

def grid_search(food,feats,weights,models=[]):
    for mod in models:
        search = GridSearchCV(mod[1],mod[2],cv=5,n_jobs=-1,
            scoring='neg_mean_absolute_error')
        search.fit(feats,weights)
        print('Food:',food)
        print('Model:',mod[0])
        print('Score:',search.best_score_)
        print('Params:',search.best_params_)

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

def main(args):
    data = prep_data(args.input_dir) 
    names = ['Lasso','Ridge','Elastic Net','Random Forest']
    models = [Lasso(),Ridge(),ElasticNet(),RandomForestRegressor()]
    params = [
        {'alpha':[1.0,5.0,10.0],
         'selection':['cyclic','random']},
        {'alpha':[1.0,5.0,10.0],
         'solver':['svd','cholesky','lsqr','sparse_cg','sag','saga','lbfgs']},
        {'alpha':[1.0,5.0,10.0],
         'l1_ratio':[0.5,0.75,0.9],
         'selection':['cyclic','random']},
        {'n_estimators':[10,50,100,200,500],
         'criterion':['squared_error','absolute_error','poisson'],
         'max_depth':[None,3,5,10],
         'min_samples_split':[2,5,10],
         'min_samples_leaf':[1,2,5,10],
         'ccp_alpha':[0.0,0.1,0.2,0.3,0.5]}]
    for k,v in data.items():
        grid_search(k,v[0],v[1],list(zip(names,models,params)))

if __name__=='__main__':
    parser = ArgumentParser()
    parser.add_argument('-i','--input_dir',default='data/ram_04-01-22')
    main(parser.parse_args())