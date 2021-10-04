# Script that integrate the whole data reading and data preparation process

import os.path as osp
import os
from Feature_Design_Timely import *
from Win_Rate_Cal import *

# Set your product pool
potprod = ['A','AG','AL', 'AU','C', 'CF', 'CS', 'CU', 'FG', 'HC', 'I', 'J', 'JD', 'JM', 'L', 'M', 'MA', 'NI', 'OI', 'P', 'PP', 'RB', 'RU', 'SR', 'TA', 'V', 'Y', 'ZC', 'ZN']

def genTrainAndTest(offset=24,s1='2014-01-01',e2='2022-01-01'):
    # Read files
    df_dict = {}
    path = osp.join(os.getcwd(), 'data')
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.h5'):
                key = file.split('_')[0]
                if key not in potprod: continue
                tmp = pd.read_hdf(osp.join(path, file))
                if len(tmp) > 360:
                    tmp = tmp.set_index('trade_date')
                    tmp['dominant_rank'] = tmp['dominant_rank'].fillna(value=0)
                    tmp = filterByDate_Flexible(tmp, start=s1, end=e2, offset=offset)
                    if len(tmp) < 60: continue
                    df_dict[key] = tmp
    key_ls = sorted(list(df_dict.keys()))
    redundant_col = ['dominant_rank', 'product_type', 'margin'] + ['tbuyv', 'tbuyvwap', 'tbuyc', 'tsellv', 'tsellvwap',
                                                                   'tsellc', 'hbid', 'lbid', 'lask', 'cbid1', 'cask1',
                                                                   'cbidv1', 'caskv1', 'clock_type', 'width',
                                                                   'offset_width', 'edge']
    for k, v in df_dict.items():
        df_dict[k] = v.drop(redundant_col, axis=1)

    # Get dataframe
    new_dict = getNewDf(df_dict,key_ls,offset)

    return df_dict,new_dict,key_ls

