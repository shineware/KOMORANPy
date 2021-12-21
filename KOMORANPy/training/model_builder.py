import math
import os
import shutil

from ..common.dictionary import Dictionary
from ..common.grammar import Grammar
from ..common.irregular.irregular_node import IrregularNode

from ..common.irregular.irregular_trie import IrregularTrie
from ..constant import SYMBOL, FILENAME
from ..parser.korean_unit_parser import KoreanUnitParser
from ..training.model.observation import Observation
from ..training.model.pos_table import PosTable
from ..training.model.transition import Transition


class ModelBuilder:
    def __init__(self):
        self.unit_parser = KoreanUnitParser()
        self.word_dic = Dictionary()
        self.irr_dic = Dictionary()
        self.grammar = Grammar()
        self.pos_table = PosTable()
        self.transition = Transition(0)
        self.observation = Observation()

    def build_path(self, path):
        self.__init__()
        self.word_dic.load(path + "/" + FILENAME.WORD_DIC)
        # todo : add external dic 부분은 구현하지 않음
        self.irr_dic.load(path + "/" + FILENAME.IRREGULAR_DIC)
        self.grammar.load(path + "/" + FILENAME.GRAMMAR)

        total_prev_pos_count = self.__get_total_prev_pos_count__()
        self._build_pos_table_(total_prev_pos_count)
        self._cal_transition_(total_prev_pos_count)
        self._cal_observation_(total_prev_pos_count)
        self._build_irregular_dic()

    def __get_total_prev_pos_count__(self):
        _pos_count_dic = {}
        for prev_pos in self.grammar.get_grammar().keys():
            cur_pos_dic = self.grammar.get_grammar()[prev_pos]
            for _cur_pos in cur_pos_dic.keys():
                _freq = 0
                if prev_pos in _pos_count_dic:
                    _freq = _pos_count_dic[prev_pos]
                _freq += cur_pos_dic[_cur_pos]
                _pos_count_dic[prev_pos] = _freq

        return _pos_count_dic

    def _build_pos_table_(self, _total_prev_pos_count):
        self.pos_table.__init__()
        for pos in _total_prev_pos_count.keys():
            self.pos_table.put(pos)
        self.pos_table.put(SYMBOL.BOE)
        self.pos_table.put(SYMBOL.EOE)
        self.pos_table.put(SYMBOL.NA)

    def _cal_transition_(self, total_prev_pos_count):
        self.transition.__init__(self.pos_table.size())
        for prev_pos in total_prev_pos_count.keys():
            cur_pos_dic = self.grammar.get_grammar().get(prev_pos)
            for cur_pos in cur_pos_dic:
                prev_to_cur_freq = cur_pos_dic.get(cur_pos)
                prev_freq = total_prev_pos_count.get(prev_pos)
                # todo : NNP인 경우에 빈도수를 뻥튀기 하는 부분은 구현하지 않음
                transition_score = prev_to_cur_freq / prev_freq
                transition_score = math.log(transition_score)
                prev_pos_id = self.pos_table.get_id(prev_pos)
                cur_pos_id = self.pos_table.get_id(cur_pos)
                self.transition.put(prev_pos_id, cur_pos_id, transition_score)
        self.transition.put(self.pos_table.get_id(SYMBOL.NA), self.pos_table.get_id(SYMBOL.EOE), -10000.0)

    def _cal_observation_(self, total_prev_pos_count):
        self.observation = Observation()
        for word in self.word_dic.get_dict():
            pos_freq_dic = self.word_dic.get_pos_freq_dict(word)
            for pos in pos_freq_dic:
                total_count = total_prev_pos_count.get(pos)
                if total_count is None:
                    print(f"{pos}가 prev pos count에 없습니다!")
                observation_score = pos_freq_dic[pos] / total_count
                observation_score = math.log(observation_score)
                self.observation.put(word, pos, self.pos_table.get_id(pos), observation_score)

    def save(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        self.transition.save(path + "/" + FILENAME.TRANSITION)
        self.observation.save(path + "/" + FILENAME.OBSERVATION)
        self.pos_table.save(path + "/" + FILENAME.POS_TABLE)
        self.irr_trie.save(path + "/" + FILENAME.IRREGULAR_MODEL)

    def _build_irregular_dic(self):
        self.irr_trie = IrregularTrie()
        for irr_pattern in self.irr_dic.get_dict():
            irr_pattern_jaso = self.unit_parser.parse(irr_pattern)
            convert_rule_freq_dic = self.irr_dic.get_dict().get(irr_pattern)
            for convert_rule in convert_rule_freq_dic:
                # todo : KOMORAN에서는 빈도수로 pruning 하는 로직이 있음
                convert_freq = convert_rule_freq_dic.get(convert_rule)
                irr_node = self.make_irr_node(irr_pattern_jaso, self.unit_parser.parse(convert_rule))
                self.irr_trie.put(irr_pattern_jaso, irr_node)

    def make_irr_node(self, irr_pattern_jaso, convert_rule_jaso):
        # todo : KOMORAN 코드 구조에서 보면 first pos id와 irregular tokens 정보만 있으면 되는 것으로 보임
        irr_node = IrregularNode()
        irr_tokens = []
        tokens = convert_rule_jaso.split(' ')
        for idx, token in enumerate(tokens):
            morph, pos = token.rsplit('/', 1)
            pos_id = self.pos_table.get_id(pos)
            if idx == 0:
                irr_node.set_first_pos_id(pos_id)
            irr_tokens.append((morph, pos_id))
        irr_node.set_tokens(irr_tokens)
        return irr_node
