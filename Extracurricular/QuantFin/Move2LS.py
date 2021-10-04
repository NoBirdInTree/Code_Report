# The dynamic two step regression (residual-based)
# It is also the up to date version

import pandas as pd
from patsy import dmatrices
from Win_Rate_Cal import *
import copy
import statsmodels.api as sm
from Add_Var import *
from Win_Rate_Cal import *
from FUNCTION_Timely_Predictor import *
import pickle

# I save the prepared dataframe cuz skewed norm takes a quite long time
(df_dict,new_dict,key_ls) = pickle.load(open('./skwed_norm_10_-1_14','rb'))
# (df_dict,new_dict,key_ls) = pickle.load(open('./norm','rb'))
# Or we could execute the function to get them
# (df_dict,new_dict,key_ls) = genTrainAndTest()

# Add variables
addVar(new_dict,key_ls)

# Get the true y dataframe
true = getGroundTrue(df_dict)

# Our test data starts from date 2015-08-01
date_set = [v.index.to_list() for k,v in new_dict.items()]
date_set = set(functools.reduce(lambda l1, l2 : l1+l2 , date_set))
date_set = np.asarray(sorted(list(date_set)))
date_set = date_set[date_set>'2015-08-01']

# i is the shift
# g1 is the time interval for model A (purely longitudinal
# g2 + com is the time interval for model B (cross-sectional
# com represented how many trade dates that model A and model B share
i = 0
g1 = 320
g2 = 100
com = 100
train_start = i
test_start = i+g1+g2
test_end = len(date_set)-1


def simpleturn(x,i=-1):
    return np.power(np.log(x),i)

str1 = 'y  ~  preRate:simpleturn(vol) + preRate_mean10:simpleturn(vol_mean10) + preRate_std25 + preRate_mean25:simpleturn(vol_mean25) + preRate_std100 + preRate_mean100:simpleturn(vol_mean100) + preRate_mean200:simpleturn(vol_mean200) + vol_mean10 + vol_mean200'
str2 = 'res  ~  chg_pct2 + g_chg_pct2 +  d_oic -1 + atr20w_3 + preRate_lmean2 + d_r'
# str2 = str2 + '+ preRate_mean5:simpleturn(vol_mean5) + preRate_std10  + vol '

full_data, _ = datasetDateFilter(new_dict, key_ls, date_set[0], date_set[-1], date_set[0], date_set[-1])
# full_data.y = full_data.y.mask(full_data.y>2,2.05)
# full_data.y = full_data.y.mask(full_data.y<-1,-0.96)
# sorted(list(set(full_data.y)))
pred = pd.DataFrame(columns=['pred','full','score'],index=date_set)
pct = 20

for i in range(0,len(date_set)-g1-g2-1):
    train_start = i
    test_start = i + g1 + g2
    if i % 300 == 0: print(f'At {i} now')
    train_data = full_data[np.logical_and(full_data.index >= date_set[train_start], full_data.index < date_set[train_start+g1])]
    y, x = dmatrices(str1, data=train_data, return_type='dataframe')
    m1 = sm.OLS(y,x).fit()

    # get res for m2
    sub_train = full_data[np.logical_and(full_data.index >= date_set[test_start-g2-com], full_data.index < date_set[test_start])]
    sub_test = full_data[full_data.index ==  date_set[test_start]]
    _, tmp_x2 = dmatrices(str1, data=sub_train, return_type='dataframe')
    _, tmp_xnew2 = dmatrices(str1, data=sub_test, return_type='dataframe')
    sub_train.loc[:,'res'] = sub_train['y'] - m1.predict(tmp_x2)
    sub_test.loc[:,'res'] = sub_test['y'] - m1.predict(tmp_xnew2)

    y2, x2 = dmatrices(str2, data=sub_train, return_type='dataframe')
    _, xnew2 = dmatrices(str2, data=sub_test, return_type='dataframe')

    m2 = sm.OLS(y2, x2).fit()
    # print(m2.summary())
    _, xnew = dmatrices(str1, data=sub_test, return_type='dataframe')
    predicted_rate = m1.predict(xnew) + m2.predict(xnew2)
    predicted_rate = pd.DataFrame(predicted_rate, index=xnew.index, columns=['fitted_value'])
    prediction = turnRateToRank(sub_test, predicted_rate, key_ls)

    # Save prediction result
    X = prediction.columns.values
    Y = prediction.iloc[0, :].values
    Z = [x for _, x in sorted(zip(Y, X),reverse=True)]
    daily_dict_rank = {j: i for i, j in zip(Y, X)}
    tmp = [float(i) for i in predicted_rate.values]
    daily_dict_score = {j: i for i, j in zip(tmp,X)}
    pred.loc[date_set[test_start],'pred'] = Z
    pred.loc[date_set[test_start],'full'] = [daily_dict_rank]
    pred.loc[date_set[test_start],'score'] = [daily_dict_score]

# Output accuracy
for i,j in [('2017-06-01','2018-01-01'),
            ('2018-01-01','2018-06-01'),
            ('2018-06-01','2019-01-01'),
            ('2019-01-01','2019-06-01'),
            ('2019-06-01','2020-01-01'),
            ('2020-01-01','2020-06-01'),
            ('2020-06-01','2021-01-01'),
            ('2021-01-01','2021-06-01')]:
    a = pred['pred'].dropna()[np.logical_and(pred.dropna().index>=i,pred.dropna().index<=j)]
    if len(a) == 0: continue
    tmp = true[:sum(true.index <= max(a.index)) + 1]
    tmp = tmp[tmp.index > min(a.index)]
    a = [i[:6] for i in a]
    highest20_true, b = getHighDifferenceGood(tmp, pct=20)
    inSample = getWinRate(a, b)
    print(f'From {i} to {j}, 6 product is',inSample)


pred.to_csv('./2LS_res2_skncomplete.csv')
# pred.to_csv('./2LS_res2_ncomplete.csv')