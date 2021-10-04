# Add variable to the dataframe

from patsy import dmatrices
from Win_Rate_Cal import *

def toabs(s):
    return s.abs()

def rollmean(s,n):
    return s.rolling(window=n).mean()

def rollstd(s,n):
    return s.rolling(window=n).std()

def lag_diff(s,n):
    return s - s.shift(n)

def lag_ratio(s,n):
    return s / s.shift(n)

def addVar(new_dict,key_ls):
    for di in [new_dict]:
        for k in key_ls:
            di[k] = di[k].dropna()

    for di in [new_dict]:
        for k in key_ls:
            di[k]['vol'] = di[k]['vol'].mask(di[k]['vol'] <= (di[k]['vol'].quantile(0.03)), di[k]['vol'].quantile(0.03))
            di[k]['vol'] = di[k]['vol'].mask(di[k]['vol'] >= (di[k]['vol'].quantile(0.97)), di[k]['vol'].quantile(0.97))
            di[k]['y'] = di[k]['preRate'].shift(-1)

    for di in [new_dict]:
        for k in key_ls:
            di[k]['y'] = di[k]['preRate'].shift(-1)

            # continue
            di[k]['preRate_std200'] = rollstd(di[k]['preRate'], 200)
            di[k]['preRate_mean200'] = rollmean(di[k]['preRate'], 200)
            di[k]['preRate_std100'] = rollstd(di[k]['preRate'], 100)
            di[k]['preRate_mean100'] = rollmean(di[k]['preRate'], 100)
            di[k]['preRate_std50'] = rollstd(di[k]['preRate'], 50)
            di[k]['preRate_mean50'] = rollmean(di[k]['preRate'], 50)
            di[k]['preRate_std25'] = rollstd(di[k]['preRate'], 25)
            di[k]['preRate_mean25'] = rollmean(di[k]['preRate'], 25)
            di[k]['preRate_std10'] = rollstd(di[k]['preRate'], 10)
            di[k]['preRate_mean10'] = rollmean(di[k]['preRate'], 10)
            di[k]['preRate_std5'] = rollstd(di[k]['preRate'], 5)
            di[k]['preRate_mean5'] = rollmean(di[k]['preRate'], 5)

            di[k]['vol_mean200'] = rollmean(di[k]['vol'], 200)
            di[k]['vol_mean100'] = rollmean(di[k]['vol'], 100)
            di[k]['vol_mean50'] = rollmean(di[k]['vol'], 50)
            di[k]['vol_mean25'] = rollmean(di[k]['vol'], 25)
            di[k]['vol_mean10'] = rollmean(di[k]['vol'], 10)
            di[k]['vol_mean5'] = rollmean(di[k]['vol'], 5)


    for di in [new_dict]:
        for k in key_ls:
            di[k]['y'] = di[k]['preRate'].shift(-1)

            di[k]['d_oi_std24'] = rollstd(di[k]['d_oi'], 24)
            di[k]['d_oi_std10'] = rollstd(di[k]['d_oi'], 10)
            di[k]['d_oi_std6'] = rollstd(di[k]['d_oi'], 6)
            di[k]['d_oi_std3'] = rollstd(di[k]['d_oi'], 3)
            di[k]['d_oic_std24'] = rollstd(di[k]['d_oic'], 24)
            di[k]['d_oic_std10'] = rollstd(di[k]['d_oic'], 10)
            di[k]['d_oic_std6'] = rollstd(di[k]['d_oic'], 6)
            di[k]['d_oic_std3'] = rollstd(di[k]['d_oic'], 3)
            di[k]['d_oic_std24'] = rollstd(di[k]['d_oic'], 24)
            di[k]['d_oic_std10'] = rollstd(di[k]['d_oic'], 10)
            di[k]['d_oic_std6'] = rollstd(di[k]['d_oic'], 6)
            di[k]['d_oic_std3'] = rollstd(di[k]['d_oic'], 3)

            di[k]['d_oi_mean24'] = rollmean(di[k]['d_oi'], 24)
            di[k]['d_oi_mean10'] = rollmean(di[k]['d_oi'], 10)
            di[k]['d_oi_mean6'] = rollmean(di[k]['d_oi'], 6)
            di[k]['d_oi_mean3'] = rollmean(di[k]['d_oi'], 3)
            di[k]['d_oic_mean24'] = rollmean(di[k]['d_oic'], 24)
            di[k]['d_oic_mean10'] = rollmean(di[k]['d_oic'], 10)
            di[k]['d_oic_mean6'] = rollmean(di[k]['d_oic'], 6)
            di[k]['d_oic_mean3'] = rollmean(di[k]['d_oic'], 3)
            di[k]['d_oic_mean24'] = rollmean(di[k]['d_oic'], 24)
            di[k]['d_oic_mean10'] = rollmean(di[k]['d_oic'], 10)
            di[k]['d_oic_mean6'] = rollmean(di[k]['d_oic'], 6)
            di[k]['d_oic_mean3'] = rollmean(di[k]['d_oic'], 3)

    for di in [new_dict]:
        for k in key_ls:
            di[k]['atr20w_3'] = rollmean(di[k]['tr'], 20) / rollmean(di[k]['close'], 15)

def addRes(m1,str,new_dict,key_ls):
    def simpleturn(x, i=-1):
        return np.power(np.log(x), i)
    for k in key_ls:
        _,x = dmatrices(str, data=new_dict[k], return_type='dataframe')
        new_dict[k]['res'] = new_dict[k]['y'] - m1.predict(x)


def datasetDateFilter(new_dict,key_ls,s1,e1,s2,e2):
    train_dict ={}
    test_dict = {}
    for k, v in new_dict.items():
        train_dict[k] = filterByDate(v, s1, e1).dropna()
        test_dict[k] = filterByDate(v, s2, e2).dropna()


    df_ls = [train_dict[k] for k in key_ls]
    df_train = functools.reduce(lambda df1, df2: pd.concat((df1, df2), axis=0), df_ls)
    df_train = df_train.dropna()

    df_ls = [test_dict[k] for k in key_ls]
    df_test = functools.reduce(lambda df1, df2: pd.concat((df1, df2), axis=0), df_ls)
    df_test = df_test.dropna()

    for i in df_train.columns:
        if not i.startswith('produ') and not i.startswith('y'):
            df_train[i] = df_train[i].astype('float64')
            df_test[i] = df_test[i].astype('float64')

    return df_train, df_test