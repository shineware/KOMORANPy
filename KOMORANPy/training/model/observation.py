
from ...common.ahocorasick.ahocorasick_dictionary import AhoCorasickDictionary
from ...parser.korean_unit_parser import KoreanUnitParser


class Observation:
    def __init__(self):
        self.ahocorasick = AhoCorasickDictionary()
        self.parser = KoreanUnitParser()

    def put(self, word, pos, pos_id, observation_score):
        korean_units = self.parser.parse(word)
        score_pos_list = self.ahocorasick.get_value(korean_units)
        if score_pos_list is None:
            # todo : KOMORAN에서는 score tag 클래스로 아래 3가지 정보를 담고 있음
            score_pos_list = [(pos, pos_id, observation_score)]
        else:
            has_same_pos = False
            for _pos, _pos_id, _observation_score in score_pos_list:
                if _pos_id == pos_id:
                    has_same_pos = True
                    break
            if not has_same_pos:
                score_pos_list.append((pos, pos_id, observation_score))
        self.ahocorasick.put(korean_units, score_pos_list)

    def get_dictionary(self):
        return self.ahocorasick

    def save(self, filename):
        self.ahocorasick.save(filename)

    def load(self, filename):
        self.ahocorasick.load(filename)
