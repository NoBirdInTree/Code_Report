import json
import re
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
# new dictionary, key is the twitter's screenname, value is the politician's name, party and other info
with open('/Users/tylerliu/N_RA/Tweet_Embedding_Polarization/info_seed_users.json', 'r') as f:
    for line in f:
        info = json.loads(line)
new_info = {}
for k,v in info.items():
    for i in v['twitter_handles']:
        new_info[i] ={'poli_name':k,'party':v['party'],'state':v['state'],'chamber':v['chamber']}
    new_info[k] = {'poli_name':k,'party':v['party'],'state':v['state'],'chamber':v['chamber']}


print('Loading tweets')
tweets = []
with open('/Users/tylerliu/data/politicians/politician_tweets_v4/politician_v4_01172021.json', 'r') as f:
  for line in f:
    tweets.append(json.loads(line))

# Drop some tweets from unknown users #!!!!! Lower case?
tweets = [tweet for tweet in tweets if (tweet['json']['user']['screen_name'] in new_info.keys())]

# replace links with "URL," and non-breaking spaces (\xa0) with normal ones
tweet_list = [tweet['json']['entities']['hashtags'] for tweet in tweets]

# Replace screen_name to the real politician's name
for i in tweets:
    i['json']['user']['screen_name'] = new_info[i['json']['user']['screen_name']]['poli_name']
user_list = [str(tweet['json']['user']['screen_name']) for tweet in tweets]


# Get the date list and set
date_list = [tweet['json']['created_at'] for tweet in tweets]
date_list = [d[4:11] + d[-4:] for d in date_list]
date_list = [datetime.strptime(d,'%b %d %Y') for d in date_list]
date_list = [d.date().toordinal() for d in date_list]
date_set = set(date_list)

date_party_user_tweets = {key: {'demo': {},'repub':{}} for  key in date_set}
demo_party = [k for k,v in new_info.items() if v['party']=='Democratic']
repub_party = [k for k,v in new_info.items() if v['party']=='Republican']
for idx,tweet in enumerate(tweet_list):
    date = date_list[idx]
    name = user_list[idx]
    if name in demo_party:
        party = 'demo'
    else:
        party = 'repub'
    if name not in date_party_user_tweets[date][party].keys():
        date_party_user_tweets[date][party][name] = [tweet]
    else:
        date_party_user_tweets[date][party][name].append(tweet)


num_of_tweets = {'demo':[],'repub':[]}
for day,day_data in date_party_user_tweets.items():
    for party,user_and_post in day_data.items():
        count = 0
        for u,p in user_and_post.items():
            count += len(p)
        num_of_tweets[party].append(count)


def dailtyToWeekly(ls):
    new_ls = []
    for idx in range(len(ls)-7):
        new_ls.append(sum(ls[idx:idx+7])/len(ls[idx:idx+6]))
    return new_ls

def DayToOrdinal(which_day):
    return datetime.strptime(which_day, '%Y-%m-%d').toordinal()


len(num_of_tweets['demo'])

days = list(date_set)
days.sort()

# Interesting
# Whether reflected in our GCN's result?

fig, ax = plt.subplots()
ax.plot_date(days,num_of_tweets['demo'],'-b',label='The daily Democratic Party\'s tweet count')
ax.plot_date(days,num_of_tweets['repub'],'-r',label='The daily Republican Party\'s tweet count')
ax.axvline(x=737732,linestyle='--',color='black')
ax.axvline(x=737773,linestyle='--',color='black')
ax.axvline(x=737767,linestyle='--',color='black')
ax.axvline(x=737782,linestyle='--',color='black')
ax.axvline(x=737797,linestyle='--',color='black')
ax.legend(loc ='upper left')

fig, ax = plt.subplots()
ax.plot_date(days[0:163],dailtyToWeekly(num_of_tweets['demo']),'-b',label='The weekly Democratic Party\'s tweet count')
ax.plot_date(days[0:163],dailtyToWeekly(num_of_tweets['repub']),'-r',label='The weekly Republican Party\'s tweet count')
ax.axvline(x=737732,linestyle='--',color='black')
ax.axvline(x=737773,linestyle='--',color='black')
ax.axvline(x=737767,linestyle='--',color='black')
ax.axvline(x=737782,linestyle='--',color='black')
ax.axvline(x=737797,linestyle='--',color='black')
ax.legend(loc ='upper left')

# The distribution of people from which we collect speeches from?
info.keys()
demo_people = 0
repub_people = 0
for k,v in info.items():
    if v['party'] == 'Republican':
        repub_people += 1
    if v['party'] == 'Democratic':
        demo_people +=  1
demo_people
repub_people

# How many tweets have hashtages
num_tweet_with_hashtags = 0
for day,day_data in date_party_user_tweets.items():
    for party,user_and_post in day_data.items():
        for u,p in user_and_post.items():
            u_hashtag_info = [i for i in p if i != []]
            num_tweet_with_hashtags += len(u_hashtag_info)
# 59235 out of 345214

# What leads to the spike?
# I investigate the hashtag usage
# Is that due to we are talking about different things?
# If it is only about different things, this effect should be alleviated by taking the average
# If we observe a strong correlation in hashtag usage, it might be reasonable to say it is the polarization,
# or divergence in the same topics that leads to such behavior

# I am still trying to come up with more concrete plans on calculating the embeddings in other ways  ()

# The hashtag usage analysis
# 1. Across 170 days
date_party_user_tweets[737807]['demo']['Pramila Jayapal']
tmp  = []
for day,day_data in date_party_user_tweets.items():
    for party,user_and_post in day_data.items():
        for u,p in user_and_post.items():
            u_hashtag_info = [i for i in p if i != []]
            for i in u_hashtag_info:
                j = i[0]['text'].lower()
                if j.__contains__('coron') or j.__contains__('covid'): tmp.append('covid')
                else: tmp.append(j)
hashtag_counter = Counter(tmp)

# 2.Daily
hashtag_counter_party_date = {key: {'demo': {},'repub':{}} for key in date_set}
for day,day_data in date_party_user_tweets.items():
    for party,user_and_post in day_data.items():
        tmp = []
        for u,p in user_and_post.items():
            u_hashtag_info = [i for i in p if i != []]
            for i in u_hashtag_info:
                j = i[0]['text'].lower()
                if j.__contains__('coron') or j.__contains__('covid'):
                    tmp.append('covid')
                else:
                    tmp.append(j)
        hashtag_counter_party_date[day][party] = Counter(tmp)

# Daily to weekly
hashtag_counter_demo_weekly =[]
hashtag_counter_repub_weekly = []
for i in range(min(date_set),max(date_set)-6+1):
    tmp1 = Counter()
    tmp2 = Counter()
    for j in range(7):
        tmp1 = tmp1 + hashtag_counter_party_date[i]['demo']
        tmp2 = tmp1 + hashtag_counter_party_date[i]['repub']
    hashtag_counter_demo_weekly.append(tmp1)
    hashtag_counter_repub_weekly.append(tmp2)

offset = min(date_set)
DayToOrdinal('2020-11-26')-offset
DayToOrdinal('2020-12-23')-offset
DayToOrdinal('2020-09-04')-offset
hashtag_counter_demo_weekly[117].most_common(20)
hashtag_counter_repub_weekly[117].most_common(20)
hashtag_counter_demo_weekly[103].most_common(20)
hashtag_counter_repub_weekly[103].most_common(20)
hashtag_counter_demo_weekly[144].most_common(20)
hashtag_counter_repub_weekly[144].most_common(20)
hashtag_counter_demo_weekly[-1].most_common(20)
hashtag_counter_repub_weekly[-1].most_common(20)
DayToOrdinal('2020-09-27')-offset
hashtag_counter_demo_weekly[53].most_common(20)
hashtag_counter_repub_weekly[53].most_common(20)
DayToOrdinal('2020-09-27')-offset
hashtag_counter_demo_weekly[75].most_common(20)
hashtag_counter_repub_weekly[75].most_common(20)

hashtag_counter_demo_weekly[34].most_common(20)
hashtag_counter_repub_weekly[34].most_common(20)


# 3.Each Party
hashtag_counter_demo = Counter()
hashtag_counter_repub = Counter()
for day,day_data in hashtag_counter_party_date.items():
    for party, party_counter in day_data.items():
        if party == 'demo': hashtag_counter_demo += party_counter
        else: hashtag_counter_repub += party_counter

hashtag_counter_demo_daily = []
hashtag_counter_repub_daily = []
for i in range(min(date_set),max(date_set)+1):
    tmp1 = Counter()
    tmp2 = Counter()
    for j in range(1):
        tmp1 = tmp1 + hashtag_counter_party_date[i]['demo']
        tmp2 = tmp1 + hashtag_counter_party_date[i]['repub']
    hashtag_counter_demo_daily.append(tmp1)
    hashtag_counter_repub_daily.append(tmp2)



# Kind of hashtag used in different group varied significantly
len(hashtag_counter_demo)
len(hashtag_counter_repub)

# Demo tends to post the post with similar content
# Repub tends to post the post with different content
demo_most_common = hashtag_counter_demo.most_common(20)
k = sum([i for i in list(hashtag_counter_demo.values()) if i >=3])
demo_most_common = [(i,j/k) for (i,j) in demo_most_common]
demo_most_common
np.var([i for i in list(hashtag_counter_demo.values()) if i >=3])

repub_most_common = hashtag_counter_repub.most_common(20)
k = sum([i for i in list(hashtag_counter_repub.values()) if i >=3])
repub_most_common = [(i,j/k) for (i,j) in repub_most_common]
repub_most_common
np.var(list(hashtag_counter_repub.values()))

# 不应该是用词的差别，底层逻辑，话题scatter导致了内部distance加大，至少从5.5W个post，从话题角度上来说，demo讨论的更加几种


# Maybe we could only consider the politician's tweets with at least one specific hashtag from the set we choose
# but I am not sure what the result would be like? 极大减少数据量（仍然可以通过avg 7天解决），不是每天都有，一些hashtag只会在一些时间出现


from scipy.stats import entropy
demp_entropy = []
repub_entropy = []
for i in range(len(hashtag_counter_demo_weekly)):
    tmp1 = dict(hashtag_counter_demo_weekly[i])
    tmp2 = dict(hashtag_counter_repub_weekly[i])
    # tmp1 = {k:v for k,v in tmp1.items() if v!=1}
    # tmp2 = {k: v for k, v in tmp2.items() if v != 1}
    a = sum(tmp1.values())
    b = sum(tmp2.values())
    t1 = [v/a for _,v in tmp1.items()]
    t2 = [v / a for _, v in tmp2.items()]
    demp_entropy.append(entropy(t1))
    repub_entropy.append(entropy(t2))

demp_entropy
repub_entropy


demp_entropy = []
repub_entropy = []
for i in range(len(hashtag_counter_demo_daily)):
    tmp1 = dict(hashtag_counter_demo_daily[i])
    tmp2 = dict(hashtag_counter_repub_daily[i])
    # tmp1 = {k:v for k,v in tmp1.items() if v!=1}
    # tmp2 = {k: v for k, v in tmp2.items() if v != 1}
    a = sum(tmp1.values())
    b = sum(tmp2.values())
    t1 = [v/a for _,v in tmp1.items()]
    t2 = [v / a for _, v in tmp2.items()]
    demp_entropy.append(entropy(t1))
    repub_entropy.append(entropy(t2))

demp_entropy
repub_entropy


import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.plot_date(days,demp_entropy,'-',label='The Democratic Party party\'s hashtag distribution entropy',color='blue')
ax.plot_date(days,repub_entropy,'-',label='The Republican Party\'s hashtag distribution entropy',color='red')
ax.legend(loc = 'upper left')
ax.axvline(x=737732,linestyle='--',color='black')
ax.axvline(x=737773,linestyle='--',color='black')
ax.axvline(x=737767,linestyle='--',color='black')
ax.axvline(x=737782,linestyle='--',color='black')
ax.axvline(x=737797,linestyle='--',color='black')
ax.grid(True)
plt.show()
