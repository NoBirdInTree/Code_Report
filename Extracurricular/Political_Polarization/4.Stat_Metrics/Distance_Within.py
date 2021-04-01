from sklearn.metrics import pairwise_distances
import matplotlib.pyplot as plt
from matplotlib.dates import drange
from datetime import datetime
import pickle
import sklearn.metrics
import json


def tols(ls):
    return [i.tolist() for i in ls]

# Return top 10 date with highest value
def getTopTenDays(ls):
    top10_days = sorted(zip(ls, days), reverse=True)[:10]
    top10_days = [b for (a, b) in top10_days]
    top10_days = [datetime.fromordinal(i).strftime('%Y-%m-%d') for i in top10_days]
    return top10_days

# Return top 10 date with lowest value
def getButtomTenDays(ls):
    top10_days = sorted(zip(ls, days), reverse=False)[:10]
    top10_days = [b for (a, b) in top10_days]
    top10_days = [datetime.fromordinal(i).strftime('%Y-%m-%d') for i in top10_days]
    return top10_days

# Average nearby data. Default is weekly (7 days interval)
def dailyToWeekly(ls, gap = 7):
    new_ls = []
    for idx in range(gap//2,len(ls)-gap//2):
        new_ls.append(sum(ls[idx-gap//2:idx+gap//2+1])/gap)
    return new_ls

metric = 'cosine'
# metric = 'euclidean'
embedding_global ={}
embedding_temporal = {}

# Your path to 170 day global embeddings
with open(f'*******/embeddings_user_party.pkl', 'rb') as f:
    embedding_global = pickle.load(f)

# Your path to daily embeddings
with open(f'/Users/tylerliu/N_RA/Tweet_Embedding_Polarization/embeddings_user_party_date.pkl', 'rb') as f:
    embedding_temporal = pickle.load(f)

# Get ur day lists
days = list(embedding_temporal.keys())
days.sort()

# temporal_inter_party cos similarity
temporal_inter_party = []
for d in days:
    embedding_day_demo = tols(embedding_temporal[d]['demo']['embeddings_list'])
    embedding_day_repub = tols(embedding_temporal[d]['repub']['embeddings_list'])
    temporal_inter_party.append(pairwise_distances(embedding_day_demo, embedding_day_repub, metric=metric).mean())

# temporal avg cos similarity
temporal_avg_party = []
for d in days:
    embedding_day_demo = tols(embedding_temporal[d]['demo']['embeddings_list'])
    embedding_day_repub = tols(embedding_temporal[d]['repub']['embeddings_list'])
    all_embeddings = embedding_day_demo + embedding_day_repub
    temporal_avg_party.append(pairwise_distances(all_embeddings, all_embeddings, metric=metric).mean())
plt.plot_date(days,temporal_avg_party,'-','bo')

# temporal_intra_party cos similarity
temporal_intra_party_demo = []
temporal_intra_party_repub = []
for d in days:
    embedding_day_demo = tols(embedding_temporal[d]['demo']['embeddings_list'])
    embedding_day_repub =  tols(embedding_temporal[d]['repub']['embeddings_list'])
    temporal_intra_party_demo.append(pairwise_distances(embedding_day_demo, embedding_day_demo, metric=metric).mean())
    temporal_intra_party_repub.append(pairwise_distances(embedding_day_repub, embedding_day_repub, metric=metric).mean())

embedding_global_demo = tols(embedding_global['demo']['embeddings_list'])
embedding_global_repub = tols(embedding_global['repub']['embeddings_list'])
embedding_global_all = embedding_global_demo + embedding_global_repub

global_avg = pairwise_distances(embedding_global_all, embedding_global_all, metric=metric).mean()
global_inter_party = pairwise_distances(embedding_global_demo, embedding_global_repub, metric=metric).mean()
global_intra_party_demo = pairwise_distances(embedding_global_demo, embedding_global_demo, metric=metric).mean()
global_intra_party_repub = pairwise_distances(embedding_global_repub, embedding_global_repub, metric=metric).mean()

global_avg
global_inter_party
global_intra_party_demo
global_intra_party_repub

# Plot daily result
fig, ax = plt.subplots()
ax.plot_date(days,temporal_intra_party_repub,'-r',label='The daily republican intra party distance')
ax.plot_date(days,temporal_intra_party_demo,'-b',label='The daily democratic intra party distance')
ax.plot_date(days,temporal_inter_party,'-',label='The daily inter party distance',color = 'coral')
ax.plot_date(days,temporal_avg_party,'-',label='The daily avg distance between all points',color = 'violet')
ax.legend(loc = 'upper left')
ax.axvline(x=737732,linestyle='--')
ax.axvline(x=737773,linestyle='--')
ax.axvline(x=737767,linestyle='--')
ax.axvline(x=737782,linestyle='--')
ax.axvline(x=737797,linestyle='--')
ax.grid(True)

# Plot weekly's result
d1 = dailyToWeekly(temporal_avg_party)
d2 = dailyToWeekly(temporal_inter_party)
d3 = dailyToWeekly(temporal_intra_party_repub)
d4 = dailyToWeekly(temporal_intra_party_demo)
fig, ax = plt.subplots()
ax.plot_date(days[3:167],d3,'-r',label='The weekly republican intra party distance')
ax.plot_date(days[3:167],d4,'-b',label='The weekly democratic intra party distance')
ax.plot_date(days[3:167],d2,'-',label='The weekly inter party distance',color = 'coral')
ax.plot_date(days[3:167],d1,'-',label='The weekly avg distance between all points',color = 'violet')
ax.axvline(x=737732,linestyle='--')
ax.axvline(x=737773,linestyle='--')
ax.axvline(x=737767,linestyle='--')
ax.axvline(x=737782,linestyle='--')
ax.axvline(x=737797,linestyle='--')
ax.legend(loc = 'upper left')
ax.grid(True)

# Plot three days' basis result
d1 = dailyToWeekly(temporal_avg_party,3)
d2 = dailyToWeekly(temporal_inter_party,3)
d3 = dailyToWeekly(temporal_intra_party_repub,3)
d4 = dailyToWeekly(temporal_intra_party_demo,3)
fig, ax = plt.subplots()
ax.plot_date(days[1:169],d3,'-r',label='The three days\' republican intra party distance')
ax.plot_date(days[1:169],d4,'-b',label='The three days\' democratic intra party distance')
ax.plot_date(days[1:169],d2,'-',label='The three days\' inter party distance',color = 'coral')
ax.plot_date(days[1:169],d1,'-',label='The three days\' avg distance between all points',color = 'violet')
ax.axvline(x=737732,linestyle='--')
ax.axvline(x=737773,linestyle='--')
ax.axvline(x=737767,linestyle='--')
ax.axvline(x=737782,linestyle='--')
ax.axvline(x=737797,linestyle='--')
ax.legend(loc = 'upper left')
ax.grid(True)



offset = min(set(days))
DayToOrdinal('2020-11-03')-offset

getTopTenDays(temporal_intra_party_repub)
getTopTenDays(temporal_intra_party_demo)


# Silhouette Score
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.metrics import silhouette_samples
silhouette_score_sample_repub_daily = []
silhouette_score_sample_demo_daily = []
silhouette_score_daily = [0]*170
silhouette_score_threedays = [0]*168
silhouette_score_weekly = [0]*164
for i in range(170):
    X1 = embedding_temporal[days[i]]['repub']['embeddings_list']
    X2 = embedding_temporal[days[i]]['demo']['embeddings_list']
    X = tols(X1+X2)
    label = [1]*len(X1) + [0]*len(X2)
    silhouette_score_daily[i] = silhouette_score(X,label,metric='cosine')
    silhouette_score_sample_repub_daily.append(sum(silhouette_samples(X,label,metric='cosine')[:len(X1)])/len(X1))
    silhouette_score_sample_demo_daily.append(sum(silhouette_samples(X, label, metric='cosine')[len(X1):]) /len(X2))
fig, ax = plt.subplots()
ax.plot_date(days,silhouette_score_daily,'-',label='The daily silhouette score over these two parties')
# ax.plot_date(days,silhouette_score_sample_repub_daily,'-',label='The daily silhouette score within repub party')
# ax.plot_date(days,silhouette_score_sample_demo_daily,'-',label='The daily silhouette score within demo party')
ax.legend(loc = 'upper left')
ax.grid(True)
plt.show()

# Daily is good, not so many ups and downs
for i in range(168):
    X1 = embedding_temporal[days[i]]['repub']['embeddings_list'] + embedding_temporal[days[i+1]]['repub']['embeddings_list'] \
         + embedding_temporal[days[i+2]]['repub']['embeddings_list']
    X1 = [i/3 for i in X1]
    X2 = embedding_temporal[days[i]]['demo']['embeddings_list'] + embedding_temporal[days[i+1]]['demo']['embeddings_list'] +\
         embedding_temporal[days[i+2]]['demo']['embeddings_list']
    X2 = [i/3 for i in X2]
    X = tols(X1+X2)
    label = [1]*len(X1) + [0]*len(X2)
    silhouette_score_threedays[i] = silhouette_score(X,label)

silhouette_score_threedays = dailyToWeekly(silhouette_score_daily,3)
silhouette_score_weekly = dailyToWeekly(silhouette_score_daily)

fig, ax = plt.subplots()
# ax.plot_date(days,silhouette_score_daily,'-',label='The daily silhouette score',color='red')
ax.plot_date(days,silhouette_score_sample_repub_daily,'-',label='The daily silhouette score within repub party',color='red')
ax.plot_date(days,silhouette_score_sample_demo_daily,'-',label='The daily silhouette score within demo party',color='blue')
ax.legend(loc = 'upper left')
ax.axvline(x=737732,linestyle='--')
ax.axvline(x=737773,linestyle='--')
ax.axvline(x=737767,linestyle='--')
ax.axvline(x=737782,linestyle='--')
ax.axvline(x=737797,linestyle='--')
ax.grid(True)
plt.show()

fig, ax = plt.subplots()
ax.plot_date(days[1:169],silhouette_score_threedays,'-',label='The three day\'s silhouette score',color='red')
ax.legend(loc = 'upper left')
ax.axvline(x=737732,linestyle='--')
ax.axvline(x=737773,linestyle='--')
ax.axvline(x=737767,linestyle='--')
ax.axvline(x=737782,linestyle='--')
ax.axvline(x=737797,linestyle='--')
ax.grid(True)

getTopTenDays(silhouette_score_daily)
getButtomTenDays(silhouette_score_daily)

getTopTenDays(silhouette_score_threedays)
getButtomTenDays(silhouette_score_threedays)
