import numpy as np
from matplotlib import pyplot as plt
from Optimization_RiksParity import *
import functools
import pickle
import pandas as pd
import ast
from Win_Rate_Cal import getGroundTrue, getAbsTrue

def getS(df):
    return df.mean()/ df.std() * np.sqrt(240)

key_ls = sorted(['A','AG','AL','AU','C','CF','CS','CU','FG','HC','I','J','JD','JM','L','M','MA','NI','OI','P','PP','RB','RU','SR','TA','V','Y','ZC','ZN'])

s = '2017-04-01'
e = '2021-06-01'

# 读取数据并根据日期过滤
def getpnldf(path):
    tmp_df = pd.read_csv(path)
    tmp_df = tmp_df.set_index('trade_date')
    tmp_df = tmp_df[key_ls]
    tmp_df = tmp_df[tmp_df.index>s]
    tmp_df = tmp_df[tmp_df.index<=e]
    return tmp_df

p_df_noloss = getpnldf('./cta_nextday_nostoploss.csv')
p_df_normal = getpnldf('./ctaall.csv')
p_df_t2 = getpnldf('./cta_nextday_stoploss0.5.csv')
p_df_t1 = getpnldf('./cta_nextday_stoploss1.csv')
p_df_t05 = getpnldf('./cta_nextday_stoploss1.5.csv')
p_df_noloss = p_df_noloss.replace(0,np.nan)
p_df_normal = p_df_normal.replace(0,np.nan)
p_df_t1 = p_df_t1.replace(0,np.nan)
p_df_t2 = p_df_t2.replace(0,np.nan)
# 针对6个产品
my_pred = pd.read_csv('./2LS_res2_skncomplete.csv')
# 针对9个产品
# my_pred = pd.read_csv('./2LS_res2_ncomplete.csv')
my_pred.columns = ['date','pred','full','score']
my_pred = my_pred.set_index('date')
my_pred = my_pred.dropna(how='all',axis=0)
my_pred = my_pred[np.logical_and(my_pred.index>=s,my_pred.index<e)]

# 选择pnl dataframe 进行计算
p_df = p_df_normal

mini_p_df = p_df[:sum(p_df.index <= max(my_pred.index)) + 1]
mini_p_df = mini_p_df[mini_p_df.index > min(my_pred.index)]

date_ls = sorted(list(my_pred.index))
red_decw_df = pd.DataFrame(0, columns=key_ls, index=mini_p_df.index)
red_minimizeRisk_df = pd.DataFrame(0, columns=key_ls, index=mini_p_df.index)

(df_dict,_,_) = pickle.load(open('./skwed_norm_10_-1_14','rb'))
abs_df = getAbsTrue(df_dict)

#选择产品个数
idx = 6
w1 = [1/idx]*idx
w2 = [6] + [7] + [12] + [3] + [2] + [1]
w2 = [i/sum(w2) for i in w2]
w3 = [40]*3 + [20]*3 + [20]*3
w3 = [i/sum(w3) for i in w3]
# 选择套用哪一个weight，根据风险，分配weight
# 风险计算依据：历史涨跌绝对值百分比
w = w3

pred = []
for p in my_pred['pred']:
    p = ast.literal_eval(p)
    pred.append(p[:idx])

i = -1
offset1 = 45
offset2 = 25

for d in red_decw_df.index:
    i = i + 1
    p = pred[i]
    p3 = p[:3]
    p6 = p[3:]
    # Step1
    where = abs_df.index.get_loc(d)
    sub_df = abs_df[where-offset1:where]
    sub_df = sub_df[p3]*1000
    tmp1 = [j for i,j in sorted(zip(sub_df.std(),p3))]

    where = abs_df.index.get_loc(d)
    sub_df = abs_df[where-offset2:where]
    sub_df = sub_df[p6]*1000
    tmp2 = [j for i,j in sorted(zip(sub_df.std(),p6))]

    p = tmp1 + tmp2
    # Step2
    where = abs_df.index.get_loc(d)
    sub_df = abs_df[where-20:where]
    sub_df = sub_df[p]*1000
    V = sub_df.cov()

    # get weights according to risk parity
    decw = get_weight(V, risk_contri=w)

    # -----------
    j = -1
    for product in p:
        profit = p_df.loc[d, product]
        profit_tight = p_df_t05.loc[d, product]
        j = j + 1
        red_decw_df.loc[d, product] = profit * decw[0, j]

# 绘图
fig, ax = plt.subplots()
(red_decw_df.sum(axis=1)).cumsum().plot()
(mini_p_df.sum(axis=1)/29).cumsum().plot()

# 计算指标
print(getS(red_decw_df.sum(axis=1)))
pnl = red_decw_df.sum(axis=1)
ret = pnl.sum() / 1000000 / len(my_pred) * 240
pnl = red_decw_df.sum(axis=1)
cumpnl = pnl.cumsum()
maxpnl = cumpnl.cummax()
drawdown = maxpnl - cumpnl
capdd = max(drawdown / 1000000)
calmar = ret / capdd
print(ret)
print(capdd)
print(calmar)
