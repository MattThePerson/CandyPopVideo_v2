from dataclasses import dataclass

from scipy.sparse import csr_matrix


@dataclass
class TFIDFModelMatrix:
    matrix: csr_matrix
    id_index_map: dict[str, int]
