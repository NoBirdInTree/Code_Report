# It is the script that contain definitions of some functions about accuracy calculation

from Tool_Box import *
import functools

def getGroundTrue(input_df,offset=None,ifabs=True):
    commodity_df_ls = []
    for k, v in input_df.items():
        if ifabs: val_change = (v.close - v.open).abs() / v.open
        else: val_change = (v.close - v.open) / v.open
        commodity_df_ls.append(pd.DataFrame(data=val_change.values, index=v.index.values, columns=[k]))
    merged_df = functools.reduce(lambda df1, df2: pd.concat([df1, df2], axis=1), commodity_df_ls).sort_index()
    rank_df = getRankDataframe(merged_df, rev=False)
    rank_df = rank_df.sort_index(axis=1)
    if offset:
        for k in rank_df.columns:
            rank_df[k] = rank_df[k].dropna().iloc[offset:]
    return rank_df

def getAbsTrue(input_df,offset=None,ifabs=True):
    commodity_df_ls = []
    for k, v in input_df.items():
        if ifabs: val_change = (v.close - v.open).abs() / v.open
        else: val_change = (v.close - v.open) / v.open
        commodity_df_ls.append(pd.DataFrame(data=val_change.values, index=v.index.values, columns=[k]))
    merged_df = functools.reduce(lambda df1, df2: pd.concat([df1, df2], axis=1), commodity_df_ls).sort_index()
    return merged_df


def turnRateToRank(predictor_df,predicted_rate,key_ls):
    X = predictor_df
    y = predicted_rate
    day_ls = sorted(set(X.index.to_list()))
    daily_rate = []
    for d in day_ls:
        tmp = []
        product_traded_at_that_day = X[X.index==d]['product'].values
        predicted_y_at_that_day = y[y.index==d][y.columns.values[0]].values
        tmp_dict = dict(zip(product_traded_at_that_day,predicted_y_at_that_day))
        for k in key_ls:
            if k not in tmp_dict.keys(): tmp.append(np.nan)
            else: tmp.append(tmp_dict[k])
        daily_rate.append(tmp)
    daily_rate_df = pd.DataFrame(daily_rate,columns=key_ls,index=day_ls)
    daily_rate_df = getRankDataframe(daily_rate_df,rev=False)
    return daily_rate_df

def getWinRate(prediction, groundTrue):
    correct_num = 0
    cum_len = 0
    if len(prediction) != len(groundTrue): print(len(prediction),len(groundTrue))
    for i in range(0,len(groundTrue)):
        pred = np.array(prediction[i])
        true = np.array(groundTrue[i])
        res = [1 if i in true else 0 for i in pred]
        correct_num = correct_num + sum(res)
        cum_len = cum_len + len(res)
    return correct_num / cum_len