import json
import os
import re

import networkx as nx
from networkx.algorithms import bipartite
import dgl

import torch

import utils

import pickle

LANGUAGE_MODEL = "roberta-large"
EMBEDDING_FOLDER = 'data/politicians/tweet_embeddings'
TIMME_FOLDER = 'data/timme/'
GRAPH_FOLDER = 'data/politicians/graphs'

if not os.path.exists(GRAPH_FOLDER):
    os.makedirs(GRAPH_FOLDER)

if not os.path.exists(TIMME_FOLDER):
    os.makedirs(TIMME_FOLDER)


# load relation data
print('Loading data')
hashtag_relations = []
retweet_relations = []
mention_relations = []
quote_relations = []
with open('data/politicians/congress_dataset_V2/congress_hashtag_relations.json', 'r') as f:
  for line in f:
    hashtag_relations.append(json.loads(line))
with open('data/politicians/congress_dataset_V2/congress_retweet_relations.json', 'r') as f:
  for line in f:
    retweet_relations.append(json.loads(line))
with open('data/politicians/congress_dataset_V2/congress_mention_relations.json', 'r') as f:
  for line in f:
    mention_relations.append(json.loads(line))
with open('data/politicians/congress_dataset_V2/congress_quote_relations.json', 'r') as f:
  for line in f:
    quote_relations.append(json.loads(line))

hashtag_user_list_g = [x['user_id'] for x in hashtag_relations]
retweet_user_list_g = [x['user_id'] for x in retweet_relations]
mention_user_list_g = [x['user_id'] for x in mention_relations]
quote_user_list_g = [x['user_id'] for x in quote_relations]
hashtag_list_g = [x['hashtag'] for x in hashtag_relations]
retweet_list_g = [x['retweeted_user_id'] for x in retweet_relations]
mention_list_g = [x['mentioned_user_id'] for x in mention_relations]
quote_list_g = [x['quoted_user_id'] for x in quote_relations]

# TODO: figure out what politician_names was used for; looks like it's never referenced again after these two lines?
with open("data/politicians/twitter_handles_seed_users.json", 'r') as f:
    politician_names = json.load(f)

congress_handles = {}
with open ("data/politicians/congress_dataset_V2/congress_users.json", 'r') as f:
    for user in map(json.loads, f.readlines()):
        congress_handles[user['json']['id_str']] = user['json']['screen_name']
congress_handles['26594419'] = 'JohnKennedyLA' # this one is missing
congress_handles['21157904'] = 'SenatorBurr'
congress_handles['23976316'] = 'RepKenMarchant'

with open("data/politicians/info_seed_users.json", 'r') as f:
    politicians = json.load(f)
handle_to_name = {}
for name, politician in politicians.items():
    for handle in politician['twitter_handles']:
        handle_to_name[handle] = name
handle_to_party = {}
for name, politician in politicians.items():
    for handle in politician['twitter_handles']:
        handle_to_party[handle] = politician['party']
handle_to_chamber = {}
for name, politician in politicians.items():
    for handle in politician['twitter_handles']:
        handle_to_chamber[handle] = politician['chamber']

# load each user's tweet embeddings
if '/' in LANGUAGE_MODEL:
    name_no_slash = LANGUAGE_MODEL.split('/')[1]
else:
    name_no_slash = LANGUAGE_MODEL
with open(f'{EMBEDDING_FOLDER}/embeddings_{name_no_slash}.pkl', 'rb') as f:
    tmp_dict = pickle.load(f)
    user_id_list = tmp_dict['user_id_list']
    embedding_list = tmp_dict['embeddings']


# construct bipartite graph: hashtag
print('Constructing hashtag graph')
B_hashtag = nx.Graph()
B_hashtag.add_nodes_from(set(hashtag_user_list_g), bipartite=0)
B_hashtag.add_nodes_from(set(hashtag_list_g), bipartite=1)

edges = zip(hashtag_user_list_g, hashtag_list_g)
B_hashtag.add_edges_from(edges)

# project back to user-user graph
intermediate_hashtag = bipartite.projected_graph(B_hashtag, set(hashtag_user_list_g), multigraph=True)

# collapse multigraph by summing edge weights
G_hashtag = nx.Graph()
for u,v,data in intermediate_hashtag.edges(data=True):
    w = data['weight'] if 'weight' in data else 1.0
    if G_hashtag.has_edge(u,v):
        G_hashtag[u][v]['weight'] += w
    else:
        G_hashtag.add_edge(u, v, weight=w)

### save graph for timmme ###
utils.save_graph_csv(G_hashtag.subgraph(user_id_list), 'user_id', 'u_user', 'count', os.path.join(TIMME_FOLDER, 'projected_hashtag_list.csv'))
###


G_hashtag = G_hashtag.to_directed()

# normalize edge weights, dividing by total in-degree
# Extra factor of 100 to help avoid too small weights/gradients. there might be a better alternative.
for n in G_hashtag.nodes():
  total_weight = G_hashtag.degree(nbunch=n,weight='weight') / 100
  for edge in G_hashtag.edges(nbunch=n, data=True):
    edge[2]['weight'] = edge[2]['weight'] / total_weight

# add node features (tweet embeddings)
G_hashtag = G_hashtag.subgraph(user_id_list)
attribute_dict = {}
for idx, key in enumerate(user_id_list):
  if key in list(G_hashtag.nodes()):
    attribute_dict[key] = embedding_list[idx]
nx.set_node_attributes(G_hashtag, attribute_dict, name='text_features')

# convert to dgl
g_hashtag = dgl.from_networkx(G_hashtag, node_attrs=['text_features'], edge_attrs=['weight'])


# now save some stuff for mapping nodes to users
node_to_id_hashtag = {i : sorted(G_hashtag.nodes())[i] for i in range(len(list(G_hashtag.nodes())))}
node_to_handle_hashtag = {node_id : congress_handles[user_id] for node_id, user_id in node_to_id_hashtag.items()}
node_to_name_hashtag = {node_id : handle_to_name[handle] for node_id, handle in node_to_handle_hashtag.items() if handle in list(handle_to_name.keys())}
node_to_party_hashtag = {node_id : handle_to_party[handle] for node_id, handle in node_to_handle_hashtag.items() if handle in list(handle_to_party.keys())}
node_to_chamber_hashtag = {node_id : handle_to_chamber[handle] for node_id, handle in node_to_handle_hashtag.items() if handle in list(handle_to_chamber.keys())}

save_dict_hashtag = {'g_hashtag':g_hashtag, 'node_to_handle_hashtag':node_to_handle_hashtag, 'node_to_name_hashtag':node_to_name_hashtag, 'node_to_party_hashtag':node_to_party_hashtag,'node_to_chamber_hashtag':node_to_chamber_hashtag}

# save
with open(f'{GRAPH_FOLDER}/hashtag_{name_no_slash}.pkl', 'wb') as f:
    pickle.dump(save_dict_hashtag, f)





# now repeat for other graph types




# construct bipartite graph: retweet
print('Constructing retweet graph')
B_retweet = nx.Graph()
B_retweet.add_nodes_from(set(retweet_user_list_g), bipartite=0)
B_retweet.add_nodes_from(set(retweet_list_g), bipartite=1)

edges = zip(retweet_user_list_g, retweet_list_g)
B_retweet.add_edges_from(edges)

# project back to user-user graph
intermediate_retweet = bipartite.projected_graph(B_retweet, set(retweet_user_list_g), multigraph=True)

# collapse multigraph by summing edge weights
G_retweet = nx.Graph()
for u,v,data in intermediate_retweet.edges(data=True):
    w = data['weight'] if 'weight' in data else 1.0
    if G_retweet.has_edge(u,v):
        G_retweet[u][v]['weight'] += w
    else:
        G_retweet.add_edge(u, v, weight=w)

### save graph for timmme ###
utils.save_timme_graph(retweet_user_list_g, retweet_list_g, user_id_list,
                       file_name=os.path.join(TIMME_FOLDER, 'retweet_list.csv'),
                       second_column='retweeted')

utils.save_graph_csv(G_retweet.subgraph(user_id_list), 'user_id', 'u_retweeted', 'count', os.path.join(TIMME_FOLDER, 'projected_retweet_list.csv'))
###


G_retweet = G_retweet.to_directed()

# normalize edge weights, dividing by total in-degree
# Extra factor of 100 to help avoid too small weights/gradients. there might be a better alternative.
for n in G_retweet.nodes():
  total_weight = G_retweet.degree(nbunch=n,weight='weight') / 100
  for edge in G_retweet.edges(nbunch=n, data=True):
    edge[2]['weight'] = edge[2]['weight'] / total_weight

# add node features (tweet embeddings)
G_retweet = G_retweet.subgraph(user_id_list)

attribute_dict = {}
for idx, key in enumerate(user_id_list):
  if key in list(G_retweet.nodes()):
    attribute_dict[key] = embedding_list[idx]
nx.set_node_attributes(G_retweet, attribute_dict, name='text_features')

# convert to dgl
g_retweet = dgl.from_networkx(G_retweet, node_attrs=['text_features'], edge_attrs=['weight'])


# now save some stuff for mapping nodes to users
node_to_id_retweet = {i : sorted(G_retweet.nodes())[i] for i in range(len(list(G_retweet.nodes())))}
node_to_handle_retweet = {node_id : congress_handles[user_id] for node_id, user_id in node_to_id_retweet.items()}
node_to_name_retweet = {node_id : handle_to_name[handle] for node_id, handle in node_to_handle_retweet.items() if handle in list(handle_to_name.keys())}
node_to_party_retweet = {node_id : handle_to_party[handle] for node_id, handle in node_to_handle_retweet.items() if handle in list(handle_to_party.keys())}
node_to_chamber_retweet = {node_id : handle_to_chamber[handle] for node_id, handle in node_to_handle_retweet.items() if handle in list(handle_to_chamber.keys())}

save_dict_retweet = {'g_retweet':g_retweet, 'node_to_handle_retweet':node_to_handle_retweet, 'node_to_name_retweet':node_to_name_retweet, 'node_to_party_retweet':node_to_party_retweet,'node_to_chamber_retweet':node_to_chamber_retweet}

# save
with open(f'{GRAPH_FOLDER}/retweet_{name_no_slash}.pkl', 'wb') as f:
    pickle.dump(save_dict_retweet, f)






# construct bipartite graph: mention
print('Constructing mention graph')
B_mention = nx.Graph()
B_mention.add_nodes_from(set(mention_user_list_g), bipartite=0)
B_mention.add_nodes_from(set(mention_list_g), bipartite=1)

edges = zip(mention_user_list_g, mention_list_g)
B_mention.add_edges_from(edges)

# project back to user-user graph
intermediate_mention = bipartite.projected_graph(B_mention, set(mention_user_list_g), multigraph=True)

# collapse multigraph by summing edge weights
G_mention = nx.Graph()
for u,v,data in intermediate_mention.edges(data=True):
    w = data['weight'] if 'weight' in data else 1.0
    if G_mention.has_edge(u,v):
        G_mention[u][v]['weight'] += w
    else:
        G_mention.add_edge(u, v, weight=w)

### save graph for timmme ###
utils.save_timme_graph(mention_user_list_g, mention_list_g, user_id_list,
                       file_name=os.path.join('mention_list.csv'),
                       second_column='mentioned')

utils.save_graph_csv(G_mention.subgraph(user_id_list), 'user_id', 'u_mentioned', 'count', os.path.join(TIMME_FOLDER, 'projected_mention_list.csv'))
###

G_mention = G_mention.to_directed()

# normalize edge weights, dividing by total in-degree
# Extra factor of 100 to help avoid too small weights/gradients. there might be a better alternative.
for n in G_mention.nodes():
  total_weight = G_mention.degree(nbunch=n,weight='weight') / 100
  for edge in G_mention.edges(nbunch=n, data=True):
    edge[2]['weight'] = edge[2]['weight'] / total_weight

# add node features (tweet embeddings)
G_mention = G_mention.subgraph(user_id_list)

attribute_dict = {}
for idx, key in enumerate(user_id_list):
  if key in list(G_mention.nodes()):
    attribute_dict[key] = embedding_list[idx]
nx.set_node_attributes(G_mention, attribute_dict, name='text_features')

# convert to dgl
g_mention = dgl.from_networkx(G_mention, node_attrs=['text_features'], edge_attrs=['weight'])


# now save some stuff for mapping nodes to users
node_to_id_mention = {i : sorted(G_mention.nodes())[i] for i in range(len(list(G_mention.nodes())))}
node_to_handle_mention = {node_id : congress_handles[user_id] for node_id, user_id in node_to_id_mention.items()}
node_to_name_mention = {node_id : handle_to_name[handle] for node_id, handle in node_to_handle_mention.items() if handle in list(handle_to_name.keys())}
node_to_party_mention = {node_id : handle_to_party[handle] for node_id, handle in node_to_handle_mention.items() if handle in list(handle_to_party.keys())}
node_to_chamber_mention = {node_id : handle_to_chamber[handle] for node_id, handle in node_to_handle_mention.items() if handle in list(handle_to_chamber.keys())}

save_dict_mention = {'g_mention':g_mention, 'node_to_handle_mention':node_to_handle_mention, 'node_to_name_mention':node_to_name_mention, 'node_to_party_mention':node_to_party_mention,'node_to_chamber_mention':node_to_chamber_mention}

# save
with open(f'{GRAPH_FOLDER}/mention_{name_no_slash}.pkl', 'wb') as f:
    pickle.dump(save_dict_mention, f)





# construct bipartite graph: quote
print('Constructing quote graph')
B_quote = nx.Graph()
B_quote.add_nodes_from(set(quote_user_list_g), bipartite=0)
B_quote.add_nodes_from(set(quote_list_g), bipartite=1)

edges = zip(quote_user_list_g, quote_list_g)
B_quote.add_edges_from(edges)

# project back to user-user graph
intermediate_quote = bipartite.projected_graph(B_quote, set(quote_user_list_g), multigraph=True)

# collapse multigraph by summing edge weights
G_quote = nx.Graph()
for u,v,data in intermediate_quote.edges(data=True):
    w = data['weight'] if 'weight' in data else 1.0
    if G_quote.has_edge(u,v):
        G_quote[u][v]['weight'] += w
    else:
        G_quote.add_edge(u, v, weight=w)


### save graph for timmme ###
utils.save_timme_graph(mention_user_list_g, mention_list_g, user_id_list,
                       file_name=os.path.join('quote_list.csv'),
                       second_column='quoted')

utils.save_graph_csv(G_quote.subgraph(user_id_list), 'user_id', 'u_quoted', 'count', os.path.join(TIMME_FOLDER, 'projected_quote_list.csv'))
###


G_quote = G_quote.to_directed()

# normalize edge weights, dividing by total in-degree
# Extra factor of 100 to help avoid too small weights/gradients. there might be a better alternative.
for n in G_quote.nodes():
  total_weight = G_quote.degree(nbunch=n,weight='weight') / 100
  for edge in G_quote.edges(nbunch=n, data=True):
    edge[2]['weight'] = edge[2]['weight'] / total_weight

# add node features (tweet embeddings)
G_quote = G_quote.subgraph(user_id_list)

attribute_dict = {}
for idx, key in enumerate(user_id_list):
  if key in list(G_quote.nodes()):
    attribute_dict[key] = embedding_list[idx]
nx.set_node_attributes(G_quote, attribute_dict, name='text_features')

# convert to dgl
g_quote = dgl.from_networkx(G_quote, node_attrs=['text_features'], edge_attrs=['weight'])


# now save some stuff for mapping nodes to users
node_to_id_quote = {i : sorted(G_quote.nodes())[i] for i in range(len(list(G_quote.nodes())))}
node_to_handle_quote = {node_id : congress_handles[user_id] for node_id, user_id in node_to_id_quote.items()}
node_to_name_quote = {node_id : handle_to_name[handle] for node_id, handle in node_to_handle_quote.items() if handle in list(handle_to_name.keys())}
node_to_party_quote = {node_id : handle_to_party[handle] for node_id, handle in node_to_handle_quote.items() if handle in list(handle_to_party.keys())}
node_to_chamber_quote = {node_id : handle_to_chamber[handle] for node_id, handle in node_to_handle_quote.items() if handle in list(handle_to_chamber.keys())}

save_dict_quote = {'g_quote':g_quote, 'node_to_handle_quote':node_to_handle_quote, 'node_to_name_quote':node_to_name_quote, 'node_to_party_quote':node_to_party_quote,'node_to_chamber_quote':node_to_chamber_quote}

# save
with open(f'{GRAPH_FOLDER}/quote_{name_no_slash}.pkl', 'wb') as f:
    pickle.dump(save_dict_quote, f)


utils.save_timme_dict(node_to_id=node_to_id_hashtag,
                      node_to_name=node_to_name_hashtag,
                      node_to_handle=node_to_handle_hashtag,
                      node_to_party=node_to_party_hashtag,
                      file_name=os.path.join(TIMME_FOLDER, 'hashtag_dict.csv'))


utils.save_timme_dict(node_to_id=node_to_id_mention,
                      node_to_name=node_to_name_mention,
                      node_to_handle=node_to_handle_mention,
                      node_to_party=node_to_party_mention,
                      file_name=os.path.join(TIMME_FOLDER, 'mention_dict.csv'))


utils.save_timme_dict(node_to_id=node_to_id_retweet,
                      node_to_name=node_to_name_retweet,
                      node_to_handle=node_to_handle_retweet,
                      node_to_party=node_to_party_retweet,
                      file_name=os.path.join(TIMME_FOLDER, 'retweet_dict.csv'))


utils.save_timme_dict(node_to_id=node_to_id_quote,
                      node_to_name=node_to_name_quote,
                      node_to_handle=node_to_handle_quote,
                      node_to_party=node_to_party_quote,
                      file_name=os.path.join(TIMME_FOLDER, 'quote_dict.csv'))