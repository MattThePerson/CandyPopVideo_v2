from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix


@dataclass
class TFIDFModel:
    vectorizer: TfidfVectorizer
    matrix: csr_matrix
    id_index_map: dict[str, int]
