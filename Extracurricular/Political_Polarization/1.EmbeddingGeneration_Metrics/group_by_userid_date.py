import json
import os
import re
from transformers import AutoModel
from transformers import AutoTokenizer
import torch
import pickle

from datetime import datetime

# Load tweets from our json file
print('Loading tweets')
tweets = []
with open('********* Your address to json file/politician_v4_01172021.json', 'r', 'r') as f:
  for line in f:
    tweets.append(json.loads(line))

# replace links with "URL," and non-breaking spaces (\xa0) with normal ones
tweet_list = [tweet['json']['text'] for tweet in tweets]
tweet_list = [re.sub('https:\/\/t\.co[\S]+','URL',tweet.replace(u'\xa0', u' ')) for tweet in tweet_list]
user_list = [str(tweet['json']['user']['id']) for tweet in tweets]

date_list = [tweet['json']['created_at'] for tweet in tweets]
date_list = [d[4:11] + d[-4:] for d in date_list]
date_list = [datetime.strptime(d,'%b %d %Y') for d in date_list]
date_list = [d.date().toordinal() for d in date_list]

# group tweets by user
date_set = set(date_list)
date_user_tweet = {key:{} for key in date_set}
for idx, tweet in enumerate(tweet_list):
  if int(user_list[idx]) not in date_user_tweet[date_list[idx]].keys():
    date_user_tweet[date_list[idx]][int(user_list[idx])]=[tweet]
  else:
    date_user_tweet[date_list[idx]][int(user_list[idx])].append(tweet)

date_embedding = {key: None for key in date_set}


device = torch.device('cuda:0')
print('Beginning embedding')

# load model
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
for day,user_tweets in date_user_tweet.items():
  counter += 1
  if counter % 10 == 0: print(f'At {counter}th day now')
  user_tweet_list = []
  user_id_list = []
  for key, value in user_tweets.items():
    user_tweet_list.append(value)
    user_id_list.append(key)
  BATCH_SIZE = 64
  embedding_list = []

  for idx, tweet_list in enumerate(user_tweet_list):
    for i in range((len(tweet_list) // BATCH_SIZE) + 1):
      batch = tweet_list[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
      if batch == []:
        continue
      tokens = tokenize(batch)
      with torch.no_grad():
        if i == 0:
          pooled = lm(**tokens.to(device), return_dict=True)['pooler_output'].detach()
        else:
          pooled = torch.cat([pooled, lm(**tokens.to(device), return_dict=True)['pooler_output'].detach()], dim=0)
    embedding_list.append(pooled.mean(dim=0).cpu())
  save_dict = {'embeddings': embedding_list, 'user_id_list': user_id_list}
  date_embedding[day] = save_dict

# Embedding is finished. Save ur result
with open(f'********* Your .pkl file', 'wb') as f:
  pickle.dump(date_embedding, f)