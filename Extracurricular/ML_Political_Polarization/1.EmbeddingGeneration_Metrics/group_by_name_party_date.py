import json
import os
import re

from transformers import AutoModel
from transformers import AutoTokenizer
import torch
from datetime import datetime

# new dictionary, key is the twitter's screenname, value is the politician's name, party and other info
# This is use to group tweets by each documented politician. Politician might have multiple userid (accounts)
with open('********* Your address to json file/info_seed_users.json', 'r') as f:
    for line in f:
        info = json.loads(line)
new_info = {}
for k,v in info.items():
    for i in v['twitter_handles']:
        new_info[i] ={'poli_name':k,'party':v['party'],'state':v['state'],'chamber':v['chamber']}
    new_info[k] = {'poli_name':k,'party':v['party'],'state':v['state'],'chamber':v['chamber']}

# Load tweets from our json file
print('Loading tweets')
tweets = []
with open('********* Your address to json file/politician_v4_01172021.json', 'r') as f:
  for line in f:
    tweets.append(json.loads(line))

# Drop some tweets from unknown users. Keep only ones for documented politician
tweets = [tweet for tweet in tweets if (tweet['json']['user']['screen_name'] in new_info.keys())]

# Replace links with "URL," and non-breaking spaces (\xa0) with normal ones
tweet_list = [tweet['json']['text'] for tweet in tweets]
tweet_list = [re.sub('https:\/\/t\.co[\S]+','URL',tweet.replace(u'\xa0', u' ')) for tweet in tweet_list]

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

date_party_user_embeddings = {key: {'demo': {'embedding_list':[],'user_list':[]},'repub':{'embedding_list':[],'user_list':[]}} for key in date_set}

# Load Model
device = torch.device('cuda:0')
LANGUAGE_MODEL = "roberta-large"
tokenizer = AutoTokenizer.from_pretrained(LANGUAGE_MODEL)
lm = AutoModel.from_pretrained(LANGUAGE_MODEL).to(device)
lm.eval()

def tokenize(batch):
        return tokenizer.batch_encode_plus(
                batch,
                add_special_tokens=True,
                padding='longest',
                return_tensors='pt',
                #max_length=MAX_SEQ_LEN,
                truncation=True
            )
BATCH_SIZE = 64
counter = -1
for day,party in date_party_user_tweets.items():
    counter += 1
    if counter % 10 == 0: print(f'At {counter}th day now')

    for k,v in party.items():
        user_name_list = []
        user_tweets_list = []
        for name,tweets in v.items():
            user_name_list.append(name)
            user_tweets_list.append(tweets)

        # Get the embedding at this day for this party!
        embedding_list =[]
        for idx, tweet_list in enumerate(user_tweets_list):
            for i in range((len(tweet_list) // BATCH_SIZE) + 1):
                batch = tweet_list[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
                if batch == []:
                    continue
                tokens = tokenize(batch)
                with torch.no_grad():
                    if i == 0:
                        pooled = lm(**tokens.to(device), return_dict=True)['pooler_output'].detach()
                    else:
                        pooled = torch.cat(
                            [pooled, lm(**tokens.to(device), return_dict=True)['pooler_output'].detach()], dim=0)
            embedding_list.append(pooled.mean(dim=0).cpu())

        save_dict = {'embeddings_list': embedding_list, 'user_name_list': user_name_list}
        date_party_user_embeddings[date][party] = save_dict

# Embedding is finished. Save ur result
with open(f'********* Your .pkl file', 'wb') as f:
  pickle.dump(date_party_user_embeddings, f)
