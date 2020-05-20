#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
use random forest classifier to guess pain state from accelerometer features
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold

# load data from .csv
df_features = pd.read_csv('~/labeled_features.csv')
df_features = df.dropna()

# partition into training and test set
data = df_features[['energy_avg','energy_dev','power1_avg','power1_dev','power2_avg','power2_dev','power3_avg','power3_dev','power4_avg','power4_dev','power5_avg','power5_dev']]
labels = df_features[['pain_score']]

x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=0)


parameter_candidates = [
  {'n_estimators': [10, 100, 500, 1000], 'max_depth': [None, 5, 10, 50], 'criterion': ['gini']},
  {'n_estimators': [10, 100, 500, 1000], 'max_depth': [None, 5, 10, 50], 'criterion': ['entropy']},
]

# Create a classifier object with the classifier and parameter candidates
clf = GridSearchCV(estimator=RandomForestClassifier(), param_grid=parameter_candidates, n_jobs=-1)

# Train the classifier on data1's feature and target data
clf.fit(x_train, y_train)

# View the accuracy score
print('Best score for data1:', clf.best_score_)

# View the best parameters for the model found using grid search
print('Best C:',clf.best_estimator_.C) 
print('Best Kernel:',clf.best_estimator_.kernel)
print('Best Gamma:',clf.best_estimator_.gamma)











