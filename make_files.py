from __future__ import division
from collections import Counter, defaultdict
import networkx as nx
import numpy as np
import pandas as pd

# import movies
df = pd.read_csv('data/imdb_edges.tsv', delimiter='\t')

# remove movies where an actor name has ? or name starts with quote
df['?'] = (df['Source'].str.startswith('\"') |
           df['Source'].str.startswith("\'") |
           df['Source'].str.contains('\?'))
movies_with_unclean_actors = df[df['?']]['Target'].unique()

# remove movies containing '#', '""', or starting with space
df['#'] = (df['Target'].str.contains('#') |
           df['Target'].str.contains('\"\"') |
           df['Target'].str.startswith(' '))
unclean_movies = df[df['#']]['Target'].unique()

# filter movies
df_clean_actors = df[~df['Target'].isin(movies_with_unclean_actors) &
                     ~df['Target'].isin(unclean_movies)]
df_clean_actors = df_clean_actors.drop(['?', '#'], axis=1)
df_clean_actors.to_csv('data/imdb_edges_clean.tsv', sep='\t', index=False)

# export clean movies
pd.DataFrame(np.sort(df_clean_actors['Source'].str.title().unique())) \
    .to_csv('data/actors.txt', index=False, header=False)

# get most common actors in graph
actor_edges = nx.read_edgelist('data/actor_edges.tsv', delimiter='\t')
degrees = actor_edges.degree()
appearances = Counter(degrees).most_common()
n_actors = len(appearances)

# assign difficulty of guessing actor based on movie appearance frequency
difficulty = defaultdict(lambda: 3)
for i, row in enumerate(appearances):
    rating = i / n_actors
    if rating <= 0.01:
        difficulty[row[0]] = 1
    elif rating <= 0.05:
        difficulty[row[0]] = 2
    else:
        difficulty[row[0]] = 3

# make imdb graph
imdb = nx.read_edgelist('data/imdb_edges_clean.tsv', delimiter='\t')
movies = np.loadtxt('data/movie_edges.tsv', dtype=str, delimiter='\t')

# assign difficulty of movie pair based on most popular actor in movie
movie_difficulty = [[movie1, movie2, min([difficulty[actor] for actor in
                    set(imdb.neighbors(movie1)) &
                    set(imdb.neighbors(movie2))])]
                    for movie1, movie2 in movies]

# export movie pairs with difficulty ratings
df = pd.DataFrame(movie_difficulty)
df.to_csv('data/movies_with_difficulty.tsv'.format(label), sep='\t',
          index=False, header=False)
