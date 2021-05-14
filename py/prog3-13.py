# -*- coding: utf-8 -*-
"""prog3-13.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1RcW5nHQrq7qBfMymJ31YAKE3RS-AkZ1U
"""

from google.colab import files
files.upload() # kaggle.jsonをアップロード
!mkdir -p ~/.kaggle
!mv kaggle.json ~/.kaggle/
!chmod 600 /root/.kaggle/kaggle.json

import pandas as pd
import numpy as np
# XGBoostをインポート
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics \
import classification_report, accuracy_score

# データの準備: アワビの物理的観測データ
def prepare():
    !kaggle datasets download -d \
    sibujohn/abalone-missing-values
    !unzip abalone-missing-values.zip

# データフレームを作成する
def makeDataFrame(add_feature=True):
    df = pd.read_csv('abalone-missing-values.csv')
    features = df.columns.values
    df = df[features]
    features = df.columns.values
    # ターゲット
    df['Sex'] = df['Sex'].map({'F':0, 'M':1, 'I':2})
    if add_feature == True:
        nf = []
        tf = {}
        for f in features: 
            c = df[f].isnull().value_counts()
            if True in c:
                nf.append('{}_NaN'.format(f))
                tf['{}_NaN'.format(f)] = df[f].isnull()
        features = np.concatenate((features, nf))
    print(features) 
    df.fillna(0, inplace=True)
    ndf = pd.DataFrame(columns=features) 
    for f in features:
        if f in df.columns: 
            ndf[f] = df[f]
        else:
            ndf[f] = tf[f]
            ndf[f] = ndf[f].map({True:1, False:0})
    print('Featues: {}'.format(len(features)))
    return ndf, features

def makeTestTrain(df):
    X = df.drop(columns='Sex')
    y = df['Sex']
    X_train, X_test, y_train, y_test = \
     train_test_split(X, y, train_size=0.9, random_state=2)
    # XGBoost用のデータ形式に変換
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test)
    return dtrain, dtest, X_train, X_test, y_train, y_test
    
def main():
    prepare()
    # 特徴量を追加しない(add_feature=False)
    df, features = makeDataFrame(add_feature=False)
    print(df)
    # XGBoost用のパラメータ
    param = {'max_depth': 2, 
             'eta': 1, 
             'objective': 'multi:softmax',
             'num_class': 3}
    # アワビの雌雄（F:雌、M:雄、I:幼生）
    target_names = ['F', 'M', 'I']
    dtrain, dtest, X_train, X_test, \
        y_train, y_test = makeTestTrain(df)
    num_round = 10
    clf = RandomForestClassifier(
             random_state=6, 
             n_estimators=50, max_depth=4)
    bst = xgb.train(param, dtrain, num_round)
    clf.fit(X_train, y_train)
    y_pred_rf = clf.predict(X_test)
    y_pred_xgb = bst.predict(dtest)
    print('not use additional feature')
    print('RF Accuracy: {:.3f}'.format( \
          accuracy_score(y_test, y_pred_rf)))
    print(classification_report(y_test, 
          y_pred_rf, target_names=target_names))
    print('XGB Accuracy: {:.3f}'.format(
          accuracy_score(y_test, y_pred_xgb)))
    print(classification_report(y_test, 
          y_pred_xgb, target_names=target_names))
    # 特徴量を追加する(add_feature=True)
    df, features = makeDataFrame(add_feature=True)
    print(df)
    dtrain, dtest, X_train, X_test, \
     y_train, y_test = makeTestTrain(df)
    bst = xgb.train(param, dtrain, num_round)
    clf = RandomForestClassifier(
          random_state=6, n_estimators=50, 
          max_depth=4)
    clf.fit(X_train, y_train)
    y_pred_rf = clf.predict(X_test)
    y_pred_xgb = bst.predict(dtest)
    print('\nuse additional feature')
    print('RF Accuracy: {:.3f}'.format( \
           accuracy_score(y_test, y_pred_rf)))
    print(classification_report(y_test, 
          y_pred_rf, target_names=target_names))
    print('XGB Accuracy: {:.3f}'.format( \
          accuracy_score(y_test, y_pred_xgb)))
    print(classification_report(y_test, 
          y_pred_xgb, target_names=target_names))

if __name__ == '__main__':
    main()