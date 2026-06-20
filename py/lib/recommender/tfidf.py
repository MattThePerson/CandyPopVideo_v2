from difflib import SequenceMatcher

import nltk
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from lib.schemas.video_data import VideoData
from lib.recommender.tfidf_model import TFIDFModel
from lib.recommender.model_matrix import TFIDFModelMatrix
from lib.recommender.stopwords_eng import STOPWORDS_ENG


def generate_tfidf_model(video_objects: list[VideoData]) -> TFIDFModel:
    tfidf_vectorizer, tfidf_matrix, hash_index_map = _build_model(video_objects)
    return TFIDFModel(
        vectorizer=tfidf_vectorizer,
        matrix=tfidf_matrix,
        id_index_map=hash_index_map,
    )


def extract_model_matrix(model: TFIDFModel) -> TFIDFModelMatrix:
    return TFIDFModelMatrix(
        matrix=model.matrix,
        id_index_map=model.id_index_map,
    )


def _build_model(video_objects: list[VideoData]) -> tuple[TfidfVectorizer, csr_matrix, dict[str, int]]:
    stemmer = SnowballStemmer('english')
    hash_index_map = {v.hash: i for i, v in enumerate(video_objects)}
    documents = []
    for i, obj in enumerate(video_objects):
        print('\rextracting tokens ({:_}/{:_}) ({:.1f}%)'.format(
            i + 1, len(video_objects), (i + 1) / len(video_objects) * 100
        ), end='')
        tokens = _extract_tokens_from_video(obj, stemmer=stemmer)
        documents.append(' '.join([''.join(t) for t in tokens]))
    print()
    model = TfidfVectorizer()
    matrix: csr_matrix = model.fit_transform(documents)  # type: ignore
    return model, matrix, hash_index_map


def get_related_videos_from_query_TFIDF(query_string: str, tfidf_model: TFIDFModel) -> list[tuple]:
    model = tfidf_model.vectorizer
    sequence_matcher = SequenceMatcher()
    stemmer = SnowballStemmer('english')
    query_tokens = _extract_tokens_from_string(query_string, stopwords=None, stemmer=stemmer, add_bigrams=True)
    query_tokens = [''.join(t) for t in query_tokens]
    for que_tok in query_tokens.copy():
        if que_tok not in model.vocabulary_:
            token_sims = [
                (vid_tok, _term_query_score(sequence_matcher, vid_tok, que_tok))
                for vid_tok in model.vocabulary_
                if vid_tok[0] == que_tok[0]
            ]
            sim_tokens = [vid_tok for vid_tok, sim in token_sims if sim > 0.8]
            query_tokens.extend(sim_tokens)
    query_vector = model.transform([' '.join(query_tokens)])[0]  # type: ignore
    return get_similar_items_cosine(query_vector, tfidf_model.matrix, tfidf_model.id_index_map)


def get_similar_items_cosine(target_vect: csr_matrix, matrix: csr_matrix, id_index_map: dict[str, int]) -> list[tuple[str, float]]:
    index_id_map = {index: hash for hash, index in id_index_map.items()}
    cosine_sims = cosine_similarity(target_vect, matrix)[0]
    sims_items = [(idx, sim) for idx, sim in enumerate(cosine_sims)]
    sims_items.sort(reverse=True, key=lambda item: item[1])
    return [(index_id_map[idx], sim) for idx, sim in sims_items]


def _extract_tokens_from_video(video: VideoData, stopwords=[], stemmer=None) -> list[tuple[str]]:
    tokens: list[tuple[str]] = []
    tokens.extend(_extract_tokens_from_string(video.title, stopwords=stopwords, stemmer=stemmer))
    tokens.extend(_extract_tokens_from_string(video.studio, stopwords=stopwords, stemmer=stemmer))
    tokens.extend(_extract_tokens_from_string(video.line, stopwords=stopwords, stemmer=stemmer))
    tokens.extend(_extract_tokens_from_string(video.description, stopwords=stopwords, stemmer=stemmer))
    tokens.extend(_extract_tokens_from_string(video.collection))
    for name in (video.actors or []):
        tokens.extend(_extract_tokens_from_string(name, stopwords=stopwords, stemmer=stemmer))
    for tag in (video.tags or []):
        tokens.extend(_extract_tokens_from_string(tag, stopwords=stopwords, stemmer=stemmer))
    return [t for t in tokens if t != '']


def _extract_tokens_from_string(string: str | None, stopwords=None, add_bigrams=True, stemmer=None) -> list[tuple[str]]:
    if not isinstance(string, str):
        return []
    for c in '.-_[](),;!?><*|#{{}}':
        string = string.replace(c, ' ')
    string = string.replace('&', 'and')
    uncamelled = [
        _camelcase_undo(word).lower()
        for word in string.split()
        if len(_camelcase_undo(word).split()) > 1
    ]
    words = [k for k in string.lower().split() if k != '']
    if stopwords:
        words = [k for k in words if k not in stopwords]
    if stemmer:
        words = [stemmer.stem(w) for w in words]
    unigrams = [(k,) for k in words if not k.isnumeric()]
    if not add_bigrams:
        return unigrams
    bigrams = [ng for ng in nltk.ngrams(words, 2) if not ng[0].isnumeric()]
    uncamelled_tokens: list[tuple[str]] = []
    for s in uncamelled:
        uncamelled_tokens.extend(_extract_tokens_from_string(s, stopwords=stopwords, add_bigrams=add_bigrams, stemmer=stemmer))
    return unigrams + bigrams + uncamelled_tokens


def _term_query_score(sequence_matcher: SequenceMatcher, a: str, b: str) -> float:
    if a == '' or b == '':
        return 0
    th = 3
    if len(a) < len(b) / th or len(a) > len(b) * th:
        return 0
    if a in b:
        return len(a) / len(b)
    elif b in a:
        return len(b) / len(a)
    sequence_matcher.set_seqs(a, b)
    return sequence_matcher.ratio()


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
