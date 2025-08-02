""" Contains dataclass for containing video data """
# HUOM: Maybe move to recommender folder. 
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix


@dataclass
class TFIDFModel:
    """ Dataclass for containing TF-IDF model vectorizer, matrix, and hash_index map """
    vectorizer: TfidfVectorizer
    matrix: csr_matrix
    id_index_map: dict[str, int]
