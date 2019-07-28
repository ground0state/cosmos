import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
import pandas as pd
import numpy as np


class RegressionModel(object):

    def __init__(self):
        self.models = []
        self.obj_col = None

    def fit(self, df):
        self.models = []
        self.obj_col = df.select_dtypes('object').columns
        if len(self.obj_col) > 0:
            df[self.obj_col] = df[self.obj_col].astype('category')

        X = df.iloc[:, 1:]
        y = df.iloc[:, 0]

        kf = KFold(n_splits=3, random_state=None, shuffle=True)
        for train_index, valid_index in kf.split(X):
            X_train, X_valid = X.iloc[train_index], X.iloc[valid_index]
            y_train, y_valid = y.iloc[train_index], y.iloc[valid_index]

            lgb_train = lgb.Dataset(X_train, y_train)
            lgb_eval = lgb.Dataset(X_valid, y_valid, reference=lgb_train)

            params = {'task': 'train',
                      'boosting_type': 'gbdt',
                      'objective': 'regression',
                      'metric': 'mse',
                      'learning_rate': 0.1,
                      'num_leaves': 20,
                      'min_data_in_leaf': 2,
                      'num_iteration': 100,
                      'verbose': 0}

            # Learning
            gbm = lgb.train(params, lgb_train, valid_sets=lgb_eval,
                            early_stopping_rounds=10)
            self.models.append(gbm)

    def predict(self, X_test):
        if len(self.obj_col) > 0:
            X_test[self.obj_col] = X_test[self.obj_col].astype('category')

        model_num = len(self.models)
        y_pred = np.zeros(len(X_test.index))

        for gbm in self.models:
            y_pred += gbm.predict(
                X_test, num_iteration=gbm.best_iteration) / model_num

        df_pred = pd.DataFrame(
            y_pred, index=X_test.index, columns=['prediction'])

        return df_pred
