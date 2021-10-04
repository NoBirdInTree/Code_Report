import math
import pickle
from Win_Rate_Cal import *
from scipy.stats import skewnorm, norm

def sd(series):
    return (series - series.mean())/series.std()

# Scan rolling window which makes every element standardized
def scan_rolling(df, offset):
    res_df = pd.DataFrame(columns=df.columns, index=df.index)
    for i in range(offset, len(df)):
        mini = df.iloc[i - offset : i-1, :]
        sum = mini.sum().sum()
        count = mini.notnull().sum().sum()
        if not sum or not count: continue
        mean = sum / count
        std = math.sqrt(((mini - mean) ** 2).sum().sum() / (count - 1))
        res_df.iloc[i-1, :] = (df.iloc[i-1, :] - mean) / std if std else np.nan
    return res_df

def turnToPercent(df):
    res_df = pd.DataFrame(columns=df.columns, index=df.index)
    for i in range(0, len(df)):
        vec = df.iloc[i, :]
        vec = vec / vec.sum()
        res_df.iloc[i, :] = vec
    return res_df

# Standardize variable globally (across different products)
def gsd(df_dict,c,offset,fun=None,relative=False):
    k_ls = list(df_dict.keys())
    df_ls = []
    for k in k_ls:
        df_ls.append(df_dict[k][c])
    df = functools.reduce(lambda df1, df2: pd.concat((df1, df2), axis=1), df_ls)
    df = df.sort_index()
    df.columns = k_ls
    if fun: df = df.apply(fun)
    if relative: df = turnToPercent(df)
    df = scan_rolling(df,offset)
    return df

# Standardize variable locally (within itself)
def lsd(df_dict,c,offset,fun=None,relative=False):
    k_ls = list(df_dict.keys())
    df_ls = []
    for k in k_ls:
        df_ls.append(df_dict[k][c])
    df = functools.reduce(lambda df1, df2: pd.concat((df1, df2), axis=1), df_ls)
    df.columns = k_ls
    if fun: df = df.apply(fun)
    if relative:
        return turnToPercent(df)
    for k in k_ls:
        mini = df[k].dropna()
        mini = (mini - mini.rolling(window=offset).mean()) / mini.rolling(window=offset).std()
        df[k] = mini
    return df

def getResponse_Plan1(df_dict,key_ls,offset=1,q=0.01,fill_mean=False,ifabs=True):
    a = 10
    b = -1
    c = 1.4
    if fill_mean == False:
        if ifabs:
            rank_df = getGroundTrue(df_dict,ifabs=True)
        else:
            rank_df = getGroundTrue(df_dict,ifabs=False)
        for i in range(0,len(rank_df)):
            vec = rank_df.iloc[i,:]
            vec = (len(key_ls)/len(vec.dropna()))*vec
            rank_df.iloc[i,:] = vec.apply(lambda x: round(x) if x>0 else np.nan)
    else:
        rank_df = getGroundTrue(df_dict)
    quantile_df = getQuantileDataframe(rank_df,lower=q,upper=1-q)
    key_ls = key_ls
    tmp_ls = []
    idx_ls = []
    for k in key_ls:
        if offset != 0:
            tmp_ls = tmp_ls + quantile_df[k].dropna().iloc[offset:,].to_list()
            idx_ls = idx_ls + quantile_df[k].dropna().iloc[offset-1:-1,].index.to_list()
        else:
            quantile_df = quantile_df.apply(lambda x: skewnorm.ppf(x, a, b, c))
            # quantile_df = quantile_df.apply(lambda x: norm.ppf(x,0,10))
            return quantile_df
    # tmp_ls = [norm.ppf(i,0,10) for i in tmp_ls]
    tmp_ls = [skewnorm.ppf(x, a, b, c) for x in tmp_ls]
    return pd.DataFrame(tmp_ls,columns=['y'],index=idx_ls),quantile_df

def getNewDf(df_dict,key_ls,offset=24):
    new_df = {k:pd.DataFrame() for k in key_ls}
    date_set = [v.index.to_list() for k, v in df_dict.items()]
    date_set = set(functools.reduce(lambda l1, l2: l1 + l2, date_set))
    date_set = sorted(list(date_set))
    new_dict = df_dict

    # volume的滑动天数
    w = 200
    vol_r = pd.DataFrame(data=None, index=date_set, columns=key_ls)
    for d in range(w, len(date_set)):
        # for d in range(w, 275):
        acc = 0
        for k in key_ls:
            idx = np.logical_and(new_dict[k].index <= date_set[d], new_dict[k].index >= date_set[d - w])
            acc = acc + new_dict[k][idx].volume.sum() if new_dict[k][idx].volume.sum() else acc
        for k in key_ls:
            idx = np.logical_and(new_dict[k].index <= date_set[d], new_dict[k].index >= date_set[d - w])
            prod_acc = new_dict[k][idx].volume.sum()
            vol_r.loc[date_set[d], k] = (
                        prod_acc / (acc * len(new_dict[k][idx].volume.dropna()) / w)) if acc and prod_acc else np.nan

    # import pickle
    # pickle.dump(vol_r,open('./w200.pkl','wb'))
    # vol_r = pickle.load(open('./w200.pkl','rb'))

    # 对一些feature进行加权，消除品种影响 ----------------------
    r = 0.75
    for k in key_ls:
        p =new_dict[k]
        index_ls = new_dict[k].index
        for i in index_ls:
            p.loc[i, 'volume'] = p.loc[i, 'volume'] / np.power(vol_r.loc[i, k], r)
            p.loc[i, 'daily_amount'] = p.loc[i, 'daily_amount'] / np.power(vol_r.loc[i, k], r)
            p.loc[i, 'daily_open_interest'] = p.loc[i, 'daily_open_interest'] / np.power(vol_r.loc[i, k], r)
            p.loc[i, 'daily_open_interest_change'] = p.loc[i, 'daily_open_interest_change'] / np.power(vol_r.loc[i, k], r)

    # 生成特征 product
    getPredictor_Product(new_df,df_dict,key_ls,offset=offset)
    # 生成特征 preY
    getPredictor_preHigh(new_df,df_dict,key_ls,offset=offset)
    # 生成特征 OHLC相关
    getPredictor_OHLC(new_df,df_dict,key_ls,offset=offset)
    # 生成特征 daily相关
    getPredictor_DailyStuff(new_df,df_dict,key_ls,offset=offset)
    getPredictor_DiffRatio(new_df,df_dict,key_ls,offset=offset)
    # 生成特征 volume相关
    getPredictor_Volume(new_df,df_dict,key_ls,offset=offset)
    # pickle.dump((df_dict,new_df,key_ls), open('skwed_norm_10_-1_14', 'wb'))
    return new_df

def getPredictor_preHigh(new_df,df_dict,key_ls,offset=1):
    preRate = getResponse_Plan1(df_dict,key_ls,offset=0,ifabs=True)
    for k in key_ls:
        new_df[k]['preRate'] = preRate[k]

def getPredictor_OHLC(new_df,df_dict,key_ls,offset=1):
    for k in key_ls:
        t = df_dict[k]
        new_df[k]['chg_pct2'] = (t.close - t.open).abs() / t.open * 100
        new_df[k]['gap'] = t.high - t.low
        new_df[k]['tr'] = pd.DataFrame((t.high - t.low,(t.high-t.close.shift(1)).abs(),(t.low-t.close.shift(1)).abs())).max()
        new_df[k]['w2'] = new_df[k]['gap'] / t.close * 10
        new_df[k]['w3'] = t.close - t.open
        new_df[k]['w6'] = new_df[k]['gap'] / t.open * 10
        new_df[k]['close'] = t.close


    g_chg_pct2 = gsd(new_df, 'chg_pct2', offset)
    g_gap = gsd(new_df, 'gap', offset)
    g_w2 = gsd(new_df, 'w2', offset)
    g_w3 = gsd(new_df, 'w3', offset)
    g_w6 = gsd(new_df, 'w6', offset)

    l_chg_pct2 = lsd(new_df, 'chg_pct2', offset)
    l_gap = lsd(new_df, 'gap', offset)
    l_w2 = lsd(new_df, 'w2', offset)
    l_w3 = lsd(new_df, 'w3', offset)
    l_w6 = lsd(new_df, 'w6', offset)

    for k in key_ls:
        new_df[k]['g_chg_pct2'] =  g_chg_pct2[k]
        new_df[k]['g_gap'] = g_gap[k]
        new_df[k]['g_w2'] = g_w2[k]
        new_df[k]['g_w3'] = g_w3[k]
        new_df[k]['g_w6'] = g_w6[k]

        new_df[k]['l_chg_pct2'] = l_chg_pct2[k]
        new_df[k]['l_gap'] = l_gap[k]
        new_df[k]['l_w2'] = l_w2[k]
        new_df[k]['l_w3'] = l_w3[k]
        new_df[k]['l_w6'] = l_w6[k]

def getPredictor_Volume(new_df,df_dict,key_ls,offset=1):

    for k in key_ls:
        new_df[k]['vol'] = df_dict[k]['volume']
        new_df[k]['volw'] = df_dict[k]['volume']
        new_df[k]['voll'] = np.log10(df_dict[k]['volume'])
        new_df[k]['vol_chg1'] = df_dict[k]['net_volume']
        new_df[k]['vol_chg2'] = df_dict[k]['net_volume'].abs()

    g_vol_meta = gsd(df_dict,'volume',offset,lambda x: np.log10(x))
    l_vol_meta = lsd(df_dict,'volume',offset,lambda x: np.log10(x))

    vol_r = lsd(df_dict, 'volume', offset, None, relative=True)

    g_vol_chg1 = gsd(df_dict,'net_volume',offset)
    l_vol_chg1 = lsd(df_dict,'net_volume',offset)
    g_vol_chg2 = gsd(new_df,'vol_chg2',offset)
    l_vol_chg2 = lsd(new_df,'vol_chg2',offset)

    for k in key_ls:
        new_df[k]['g_vol_meta'] = g_vol_meta[k]
        new_df[k]['l_vol_meta'] = l_vol_meta[k]
        new_df[k]['vol_r'] = vol_r[k]
        new_df[k]['vol_scaler1'] = np.log10(np.log10(new_df[k]['vol']))
        new_df[k]['vol_scaler2'] = np.power(np.log10(new_df[k]['vol']),-1)
        new_df[k]['g_vol_chg1'] = g_vol_chg1[k]
        new_df[k]['l_vol_chg1'] = l_vol_chg1[k]
        new_df[k]['g_vol_chg2'] = g_vol_chg2[k]
        new_df[k]['l_vol_chg2'] = l_vol_chg2[k]

    g_vol_r = gsd(new_df, 'vol_r', offset)
    l_vol_r = lsd(new_df, 'vol_r', offset)
    for k in key_ls:
        new_df[k]['g_vol_r'] = g_vol_r[k]
        new_df[k]['l_vol_r'] = l_vol_r[k]


def getPredictor_DailyStuff(new_df,df_dict,key_ls,offset=1):
    for k in key_ls:
        new_df[k]['d_a'] = df_dict[k]['daily_amount']
        new_df[k]['d_oi'] = np.log10(df_dict[k]['daily_open_interest'])
        new_df[k]['d_oic'] = np.cbrt(df_dict[k]['daily_open_interest_change'])
        new_df[k]['d_pct3'] = df_dict[k]['daily_amount'] / df_dict[k]['volume']
    l_d_oi = lsd(df_dict,'daily_open_interest',offset,lambda x: np.log10(x))
    l_d_oic = lsd(df_dict, 'daily_open_interest_change', offset)
    g_d_oi = gsd(df_dict,'daily_open_interest',offset,lambda x: np.log10(x))
    g_d_oic = gsd(df_dict, 'daily_open_interest_change', offset)
    g_d_pct3 = gsd(new_df, 'd_pct3', offset)
    l_d_pct3 = lsd(new_df, 'd_pct3', offset)

    d_r = lsd(df_dict, 'daily_amount', offset, None, relative=True)

    for k in key_ls:
        new_df[k]['l_d_oi'] = l_d_oi[k]
        new_df[k]['l_d_oic'] = l_d_oic[k]
        new_df[k]['g_d_oi'] = g_d_oi[k]
        new_df[k]['g_d_oic'] = g_d_oic[k]
        new_df[k]['g_d_pct3'] = g_d_pct3[k]
        new_df[k]['l_d_pct3'] = l_d_pct3[k]
        new_df[k]['d_r'] = d_r[k]

    l_d_r = lsd(new_df, 'd_r', offset)
    g_d_r = gsd(new_df, 'd_r', offset)
    for k in key_ls:
        new_df[k]['l_d_r'] = l_d_r[k]
        new_df[k]['g_d_r'] = g_d_r[k]

def getPredictor_DiffRatio(new_df,df_dict,key_ls,offset=1):
    for k in key_ls:
        new_df[k]['diff_ratio'] = df_dict[k]['ratio']
        new_df[k]['diff_amount'] = df_dict[k]['diff']

def getPredictor_Product(new_df,df_dict,key_ls,offset=1):
    for k in key_ls:
        new_df[k]['product'] = df_dict[k]['product'].str.split('_').str[0]