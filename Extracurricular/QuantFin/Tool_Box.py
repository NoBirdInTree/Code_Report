# It is the script that contain definitions of some functions about data processing

import pandas as pd
import numpy as np

def getRankDataframe(input_df,rev = False):
    def calculate_rank(vector):
        a = {}
        rank = 1
        for num in sorted(vector.dropna().to_list(),reverse=rev):
            if num not in a:
                a[num] = rank
                rank = int(rank + 1)
        res = [a[i] if i >-99 else np.nan for i in vector]
        return res

    rank_ls = []
    for i in range(0,len(input_df)):
        vec = input_df.iloc[i,:]
        rank_ls.append(calculate_rank(vec))

    return pd.DataFrame(rank_ls,index=input_df.index, columns=input_df.columns)

def getQuantileDataframe(input_df,lower=0.05,upper=0.95):
    l = lower
    u = upper
    for i in range(0,len(input_df)):
        a = input_df.iloc[i,:]
        a = (a - min(a.dropna())) / (max(a.dropna()) - min(a.dropna()))
        a = a * (u - l) + l
        input_df.iloc[i,:] = a
    return input_df

def filterByDate(input_df,start,end):
    return input_df[np.logical_and(input_df.index>start,input_df.index<end)]

def filterByDate_Flexible(input_df,start,end,offset):
    idx = np.where(np.logical_and(input_df.index >= start, input_df.index < end) == True)[0]
    s = idx[0]
    e = idx[-1]
    if input_df.index[0] < input_df.index[s]:
        return input_df.iloc[s-offset+1:e+1]
    else:
        return input_df[np.logical_and(input_df.index > start, input_df.index < end)]

def getLowDifferenceGood(input_df,pct=None,count=5):
    # calculate yes or no the most ?% volatile dataframe
    df = []
    if pct:
        for i in range(0, len(input_df)):
            cut_off = len(input_df.iloc[i,:].dropna()) * pct / 100
            vec = input_df.iloc[i, :].to_list()
            vec = [1 if i <= cut_off else 0 for i in vec]
            df.append(vec)
    else:
        for i in range(0, len(input_df)):
            cut_off = sorted(input_df.iloc[i,:].dropna())[count-1] if count <= len(input_df.iloc[i,:].dropna()) else sorted(input_df.iloc[i,:].dropna())[-1]
            vec = input_df.iloc[i, :].to_list()
            vec = [1 if i <= cut_off else 0 for i in vec]
            df.append(vec)
    high_df = pd.DataFrame(df, index=input_df.index, columns=input_df.columns)
    return high_df

def getHighDifferenceGood(input_df,pct=None,count=5):
    # calculate yes or no the least ?% volatile dataframe
    df = []
    record_ls = []
    c = input_df.columns.values
    if pct:
        for i in range(0, len(input_df)):
            how_many = round(len(input_df.iloc[i,:].dropna()) * pct/100)
            cut_off = sorted(input_df.iloc[i,:].dropna())[-how_many] if max(input_df.iloc[i, :].dropna()) > 2.01 else 1.5
            # if i == 844: print(cut_off,len(input_df.iloc[i,:].dropna()))
            vec = input_df.iloc[i, :].to_list()
            new_vec = []
            for i in vec:
                if i- cut_off >= -0.0001: new_vec.append(1)
                elif i< cut_off: new_vec.append(0)
                else: new_vec.append(np.nan)
            df.append(new_vec)
            tmp = [c[idx] for idx,i in enumerate(new_vec) if i == 1]
            record_ls.append(tmp)
    else:
        for i in range(0, len(input_df)):
            cut_off = sorted(input_df.iloc[i, :].dropna())[-count] if count <= len(input_df.iloc[i,:].dropna()) else sorted(input_df.iloc[i,:].dropna())[0]
            vec = input_df.iloc[i, :].to_list()
            vec = [1 if i >= cut_off else 0 for i in vec]
            df.append(vec)
    df = pd.DataFrame(df, index=input_df.index, columns=input_df.columns)
    return df,record_ls

def dropAllZeroColoumn(df):
    df = df.replace(0, np.nan).dropna(axis=1, how="all")
    return df.replace(np.nan,0)