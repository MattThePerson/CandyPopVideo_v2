""" functions for TF-IDF related stuff """
from difflib import SequenceMatcher
import numpy as np
import nltk
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from src.schemas import TFIDFModel, VideoData

with open('data/stopwords_eng.txt', 'r') as f:
    STOPWORDS_ENG = [ line.strip() for line in f ]


def generate_tfidf_model(video_objects: list[VideoData]) -> TFIDFModel:
    """ Generates tfidf model object, tfidf matrix and hash-index map for TF-IDF model of video objects and returns as dict """
    tfidf_vectorizer, tfidf_matrix, hash_index_map = _generate_tfidf_model_for_videos(video_objects)
    return TFIDFModel(
        vectorizer =     tfidf_vectorizer,
        matrix =         tfidf_matrix,
        id_index_map = hash_index_map,
    )

def _generate_tfidf_model_for_videos(video_objects: list[VideoData]) -> tuple[TfidfVectorizer, csr_matrix, dict[str, int]]:
    """ Generates tfidf model object, tfidf matrix and hash-index map for TF-IDF model of video objects """
    stemmer = SnowballStemmer('english')
    hash_index_map = { v.hash: i for i, v in enumerate(video_objects) }
    documents = []
    for i, obj in enumerate(video_objects):
        print('\rextracting tokens ({:_}/{:_}) ({:.1f}%)'.format(i+1, len(video_objects), (((i+1)/len(video_objects)*100))), end='')
        tokens = _extract_tokens_from_video_object(obj, stemmer=stemmer)
        doc = ' '.join([ ''.join(t) for t in tokens ])
        documents.append(doc)
    print()
    model = TfidfVectorizer()
    matrix: csr_matrix = model.fit_transform(documents) # type: ignore (thinks its spmatrix so complains about indexing)
    vector = matrix[0]
    return model, matrix, hash_index_map


def get_related_videos_from_query_TFIDF(query_string: str, tfidf_model: TFIDFModel) -> list[tuple]:
    """ Given a string, returns list of related video """
    model = tfidf_model.vectorizer
    sequence_matcher = SequenceMatcher()
    # stopwords_eng = stopwords.words('english')
    stemmer = SnowballStemmer('english')
    query_tokens = _extract_tokens_from_string(query_string, stopwords=None, stemmer=stemmer, add_bigrams=True)
    query_tokens = [ ''.join(t) for t in query_tokens ]
    for que_tok in query_tokens.copy():
        if que_tok not in model.vocabulary_:
            print('NOT IN VOCAB:', que_tok)
            token_sims = [ (vid_tok, _term_query_score(sequence_matcher, vid_tok, que_tok)) for vid_tok in model.vocabulary_ if (vid_tok[0] == que_tok[0]) ]# if ( len(vid_tok) == len(que_tok) and vid_tok[0][0] == que_tok[0][0] ) ]
            sim_tokens = [ vid_tok for vid_tok, sim in token_sims if sim > 0.8 ]
            print(sim_tokens)
            query_tokens.extend(sim_tokens)
    query_vector = model.transform([' '.join(query_tokens)])[0] # type: ignore (complains about indexing spmatrix)
    sims_items = get_similar_items_TFIDF(query_vector, tfidf_model.matrix, tfidf_model.id_index_map)
    return sims_items


def get_similar_videos_for_hash_TFIDF(video_hash: str, tfidf_model: TFIDFModel) -> list[tuple]:
    matrix, hash_index_map = tfidf_model.matrix, tfidf_model.id_index_map
    video_index = hash_index_map.get(video_hash)
    if video_index is None:
        return []
    target_vector = matrix[video_index]
    sims_items = get_similar_items_TFIDF(target_vector, matrix, hash_index_map)
    return sims_items


def get_similar_items_TFIDF(target_vect: csr_matrix, matrix: csr_matrix, id_index_map: dict[str, int]) -> list[tuple]:
    index_id_map = { index: hash for hash, index in id_index_map.items() }
    cosine_sims = cosine_similarity(target_vect, matrix)[0]
    sims_items = [ (idx, sim) for idx, sim in enumerate(cosine_sims) ]
    sims_items.sort(reverse=True, key=lambda item: item[1])
    sims_ids = [ (index_id_map[idx], sim) for idx, sim in sims_items ]
    return sims_ids


def get_similar_items_TFIDF_dot(target_vect: csr_matrix, matrix: csr_matrix, id_index_map: dict[str, int]) -> list[tuple]:
    index_id_map = { index: hash for hash, index in id_index_map.items() }
    dot_sims = _dot_similarity(target_vect, matrix)
    sims_items = [ (i, sim) for i, sim in enumerate(dot_sims) ]
    sims_items.sort( reverse=True, key=lambda item: item[1] )
    sims_ids = [ (index_id_map[i], sim) for i, sim in sims_items ]
    return sims_ids


def _dot_similarity(target_vect: csr_matrix, matrix: csr_matrix):
    dot_sims = matrix.dot(target_vect.T).toarray().ravel()
    return dot_sims


# TODO: remove
# [TOKEN-MAP MODEL] Simple but handles non key tokens
# def get_related_hashes_from_query(token_hashes, query):
#     sequence_matcher = SequenceMatcher()
#     stopwords = None#stopwords.words('english')
#     stemmer = SnowballStemmer('english')
#     query_tokens = _extract_tokens_from_string(query, stopwords=stopwords, stemmer=stemmer, add_bigrams=True)
#     query_token_weights = { t: np.sqrt(query_tokens.count(t)) for t in sorted(set(query_tokens)) } # sqrt to flatten out score of multiple tokens
#     unique_hashes_amount = len(set([h for hashes in token_hashes.values() for h in hashes]))
#     hash_scores = {}
#     queue = list(query_token_weights.keys()).copy()
#     # for que_tok in query_token_weights.keys():
#     while queue != []:
#         que_tok = queue.pop()
#         hashes_for_token = token_hashes.get(que_tok)
#         if hashes_for_token == None:
#             token_sims = [ (vid_tok, _token_similarity(vid_tok, que_tok, sequence_matcher)) for vid_tok in token_hashes.keys() if ( len(vid_tok) == len(que_tok) and vid_tok[0][0] == que_tok[0][0] ) ]
#             token_sims.sort(reverse=True, key=lambda x: x[1])
#             counter = 0
#             for vid_tok, sim in token_sims:
#                 if sim < 0.4 or counter > 96:
#                     break
#                 query_token_weights[vid_tok] = sim * query_token_weights[que_tok]
#                 queue.append(vid_tok)
#                 counter += len(token_hashes.get(vid_tok))
#             query_token_weights[que_tok] = 0
#         if hashes_for_token:
#             for hash in hashes_for_token:
#                 hash_scores[hash] = hash_scores.get(hash, 0) + query_token_weights.get(que_tok) * np.log(unique_hashes_amount / len(hashes_for_token))
#     results = [ (hash, score) for hash, score in hash_scores.items() if score > 0 ]
#     results = sorted(results, reverse=True, key=lambda res: res[1])
#     return results, query_token_weights


#### TOKEN FUNCTIONS

def _extract_tokens_from_video_object(video: VideoData, stopwords=[], stemmer=None) -> list[tuple[str]]:
    tokens: list[tuple[str]] = []
    tokens.extend( _extract_tokens_from_string( video.title,          stopwords=stopwords, stemmer=stemmer) )
    tokens.extend( _extract_tokens_from_string( video.studio,               stopwords=stopwords, stemmer=stemmer) )
    tokens.extend( _extract_tokens_from_string( video.line,                 stopwords=stopwords, stemmer=stemmer) )
    tokens.extend( _extract_tokens_from_string( video.description,    stopwords=stopwords, stemmer=stemmer) )
    tokens.extend( _extract_tokens_from_string( video.collection ) )
    for name in video.actors:
        tokens.extend( _extract_tokens_from_string(name, stopwords=stopwords, stemmer=stemmer) )
    for tag in video.tags:
        tokens.extend( _extract_tokens_from_string(tag, stopwords=stopwords, stemmer=stemmer) )
    return [ t for t in tokens if t != '' ]


# get ngrams after stopword removal and stemming
def _extract_tokens_from_string(string: str|None, stopwords=None, add_bigrams=True, stemmer=None) -> list[tuple[str]]:
    if not isinstance(string, str):
        return []
    for c in '.-_[](),;!?><*|#{{}}':
        string = string.replace(c, ' ')
    string = string.replace('&', 'and')
    uncamelled = [ _camelcase_undo(word).lower() for word in string.split() if len(_camelcase_undo(word).split()) > 1 ] # hold for later
    words = [ k for k in string.lower().split() if (k != '') ]
    if stopwords:
        words = [ k for k in words if (k not in stopwords) ]
    if stemmer:
        words = [ stemmer.stem(w) for w in words ]
    unigrams = [ (k,) for k in words if not k.isnumeric() ]
    if not add_bigrams:
        return unigrams
    bigrams = [ ng for ng in nltk.ngrams(words, 2) if not ng[0].isnumeric() ]
    uncamelled_tokens = []
    for s in uncamelled:
        uncamelled_tokens.extend( _extract_tokens_from_string(s, stopwords=stopwords, add_bigrams=add_bigrams, stemmer=stemmer) )
    return unigrams + bigrams + uncamelled_tokens


# assumes inputs are lower case
def _term_query_score(sequence_matcher: SequenceMatcher, a: str, b: str) -> float:
    if a == '' or b == '':
        return 0
    th = 3
    if len(a) < len(b)/th or len(a) > len(b)*th:
        return 0
    if a in b:
        return len(a) / len(b)
    elif b in a:
        return len(b) / len(a)
    sequence_matcher.set_seqs(a, b)
    score = sequence_matcher.ratio()
    return score
    if score >= 0.7:
        return score
    return 0


# 
def _token_similarity(t1, t2, sm):
    return _term_query_score(sm, ' '.join(t1), ' '.join(t2))



def _camelcase_undo(string: str):
    chars = []
    flag = False
    for c in string:
        if c.isupper():
            if chars != [] and not flag:
                chars.append(' ')
            flag = True
        else:
            flag = False
        chars.append(c)
    return ''.join(chars)
