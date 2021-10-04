import os
import sys

import json
import pandas as pd
import numpy as np

import torch
from torch import nn
import torch.nn.functional as F

import dgl
import dgl.function as fn

import pickle


graph_type = sys.argv[1]
if graph_type not in ['hashtag','retweet','mention', 'follower', 'quote']:
    raise NameError('unknown graph type. Currently allowed types: hashtag, retweet, mention, follower, quote')

LANGUAGE_MODEL = "roberta-large"
GRAPH_FOLDER = 'data/politicians/graphs'
GRAPH_EMBEDDING_FOLDER = 'data/politicians/graph_embeddings'

if not os.path.exists(GRAPH_EMBEDDING_FOLDER):
    os.makedirs(GRAPH_EMBEDDING_FOLDER)

device = torch.device('cuda:0')

# load graphs
if '/' in LANGUAGE_MODEL:
    name_no_slash = LANGUAGE_MODEL.split('/')[1]
else:
    name_no_slash = LANGUAGE_MODEL
with open(f'{GRAPH_FOLDER}/{graph_type}_{name_no_slash}.pkl', 'rb') as f:
    save_dict = pickle.load(f)
g = save_dict[f'g_{graph_type}'].to(device)

node_to_name = save_dict[f'node_to_name_{graph_type}']
node_to_handle = save_dict[f'node_to_handle_{graph_type}']
node_to_party = save_dict[f'node_to_party_{graph_type}']
node_to_chamber = save_dict[f'node_to_chamber_{graph_type}']

# load stuff and compute which handle is the most active (most tweets) for politicians with multiple
with open("data/politicians/twitter_handles_seed_users.json", 'r') as f:
    politician_names = json.load(f)
handle_to_id = {} # str(twitter_handle) : str(twitter_id) 
with open ("data/politicians/congress_dataset_V2/congress_users.json", 'r') as f:
    for user in map(json.loads, f.readlines()):
        handle_to_id[user['json']['screen_name']] = user['json']['id_str']
handle_to_id['JohnKennedyLA'] = '26594419' # this one is missing

with open("data/politicians/info_seed_users.json", 'r') as f:
    politicians = json.load(f)
name_to_handle = {}
for name, politician in politicians.items():
    name_to_handle[name] = politician['twitter_handles']

# count tweets by handle
tweets = []
with open('data/politicians/politician_tweets_v3/politician_v3_12132020.json', 'r') as f:
  for line in f:
    tweets.append(json.loads(line))
tweet_list = [tweet['json']['text'] for tweet in tweets]
user_list = [str(tweet['json']['user']['id']) for tweet in tweets]
user_set = set(user_list)
user_tweets = {key : [] for key in user_set}
for idx, tweet in enumerate(tweet_list):
  user_tweets[user_list[idx]].append(tweet)
user_tweet_counts = {key:len(value) for key, value in user_tweets.items()} # str(twitter_id) : int(count)
handle_to_counts = {handle : user_tweet_counts[twitter_id] for handle, twitter_id in handle_to_id.items() if twitter_id in user_tweet_counts}

# make a list of most active
most_active_handles = []
for name, handle_list in name_to_handle.items():
    if len(handle_list) == 1:
        most_active_handles.append(handle_list[0])
    elif len(handle_list) == 0:
        continue
    else:
        count_list = [handle_to_counts[handle] if handle in handle_to_counts else 0 for handle in handle_list]
        arg_max_count = np.argmax(count_list)
        most_active_handles.append(handle_list[arg_max_count])



# gcn adapted from https://docs.dgl.ai/guide/training-link.html
gcn_msg = fn.u_mul_e('h', 'weight', 'm') 
#gcn_msg = fn.copy_src(src='h', out='m') # <- uncomment for unweighted
gcn_reduce = fn.sum(msg='m', out='h')

class GCNLayer(nn.Module):
    def __init__(self, in_feats, out_feats):
        super(GCNLayer, self).__init__()
        self.linear = nn.Linear(in_feats, out_feats)

    def forward(self, g, feature):
        # Creating a local scope so that all the stored ndata and edata
        # (such as the `'h'` ndata below) are automatically popped out
        # when the scope exits.
        with g.local_scope():
            g.ndata['h'] = feature
            g.update_all(gcn_msg, gcn_reduce)
            h = g.ndata['h']
            return self.linear(h)

class DotProductPredictor(nn.Module):
    def forward(self, graph, h):
        # h contains the node representations computed from the GNN defined
        # in the node classification section (Section 5.1).
        with graph.local_scope():
            graph.ndata['h'] = h
            graph.apply_edges(fn.u_dot_v('h', 'h', 'score'))
            return graph.edata['score']

def construct_negative_graph(graph, k):
    src, dst = graph.edges()
    weights = graph.edata['weight']

    neg_src = src.repeat_interleave(k)
    neg_dst = torch.randint(0, graph.number_of_nodes(), (len(src) * k,)).to(device)
    neg_graph = dgl.graph((neg_src, neg_dst), num_nodes=graph.number_of_nodes())
    neg_graph.edata['weight'] = torch.rand((len(src) * k,)).to(device)
    #weight_indexer = torch.randint(0, graph.number_of_nodes(), (len(src) * k,))
    #neg_graph.edata['weight'] = weights[weight_indexer].to(device)
    return neg_graph

class Model(nn.Module):
    def __init__(self, g, in_features, hidden_features, out_features):
        super().__init__()
        self.sage = GCNLayer(in_features, out_features) # SAGE(in_features, hidden_features, out_features)
        self.pred = DotProductPredictor()
    def forward(self, g, neg_g, x):
        h = self.sage(g, x)
        return self.pred(g, h), self.pred(neg_g, h)

def bce_loss(scores, labels):
    return F.binary_cross_entropy_with_logits(scores.flatten(), labels.flatten())

def l2_loss(scores, labels):
    return F.mse_loss(scores.flatten(), labels.flatten())

def compute_loss(pos_score, neg_score):
    n_edges = pos_score.size(0) # pos_score => n_edges x 1
    neg_score = neg_score.view(n_edges, -1) # n_edges x neg_samples

    pos_labels = torch.ones_like(pos_score)
    neg_labels = torch.zeros_like(neg_score)

    combined_scores = torch.cat([pos_score, neg_score], dim=-1) # n_edges x (1+neg_samples)
    combined_labels = torch.cat([pos_labels, neg_labels], dim=-1) # ^^^

    loss = bce_loss(combined_scores, combined_labels)

    return loss

print(f'Training GCN: {graph_type}')

#g.ndata['text_features'] = torch.eye(g.ndata['text_features'].shape[0]).to(device) # <- to try without text embeddings
node_features = g.ndata['text_features']
n_features = node_features.shape[1]
k = 5
model = Model(g, n_features, 100, 100).to(device)
opt = torch.optim.Adam(model.parameters())
for epoch in range(1000):
    negative_graph = construct_negative_graph(g, k)
    pos_score, neg_score = model(g, negative_graph, node_features)
    loss = compute_loss(pos_score, neg_score)
    #pos_score = model(g, g, node_features)
    #loss = l2_loss(pos_score, g.edata['weight'])
    opt.zero_grad()
    loss.backward()
    opt.step()
    if epoch % 250 == 0:
        print(epoch, loss.item())
print(loss.item())


node_embeddings = model.sage(g, node_features).detach().cpu().numpy()
#node_embeddings = node_features.detach().cpu().numpy() # <- to try without graph

# filter embeddings by most active handle when there's multiple
new_node_to_name = {}
embeddings_by_name = {}
for nid, name in node_to_name.items():
    if node_to_handle[nid] in most_active_handles:
        embeddings_by_name[name] = node_embeddings[nid]
        new_node_to_name[nid] = name

save_dict['embeddings_by_name'] = embeddings_by_name
save_dict['node_to_name'] = new_node_to_name
save_dict['node_embeddings'] = node_embeddings

# save
with open(f'{GRAPH_EMBEDDING_FOLDER}/{graph_type}.pkl', 'wb') as f:
    pickle.dump(save_dict, f)