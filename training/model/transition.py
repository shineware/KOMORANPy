import numpy as np
import pickle
import gzip


class Transition:
    def __init__(self, size):
        self.score_matrix = np.full((size, size), -np.inf)

    def put(self, prev_pos_id, cur_pos_id, score):
        self.score_matrix[prev_pos_id][cur_pos_id] = score

    def get(self, prev_pos_id, cur_pos_id):
        score = self.score_matrix[prev_pos_id][cur_pos_id]
        if score == -np.inf:
            return None
        return score

    def save(self, filename):
        with gzip.open(filename, 'wb') as f:
            pickle.dump(self.score_matrix, f)

    def load(self, filename):
        with gzip.open(filename, 'rb') as f:
            self.score_matrix = pickle.load(f)
