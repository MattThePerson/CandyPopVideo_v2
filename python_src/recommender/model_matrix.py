""" Contains dataclass for containing video data """
from typing import Any
from dataclasses import dataclass

from scipy.sparse import csr_matrix


@dataclass
class TFIDFModelMatrix:
    """ Dataclass for containing TF-IDF model matrix and hash_index map """
    matrix: csr_matrix
    id_index_map: dict[str, int]
