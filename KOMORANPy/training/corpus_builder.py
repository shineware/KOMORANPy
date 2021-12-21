import os
import re
import shutil

from ..common.dictionary import Dictionary
from ..common.grammar import Grammar
from ..constant import SYMBOL, FILENAME
from ..parser.corpus_parser import CorpusParser
from ..parser.irregular_parser import IrregularParser
from ..parser.korean_unit_parser import KoreanUnitParser, is_jamo


class CorpusBuilder:
    def __init__(self):
        self.unit_parser = KoreanUnitParser()
        self.corpus_parser = CorpusParser()
        self.irregular_parser = IrregularParser()
        self.word_dic = Dictionary()
        self.irr_dic = Dictionary()
        self.grammar = Grammar()

    def save(self, path):
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        self.word_dic.save(path + "/" + FILENAME.WORD_DIC)
        self.irr_dic.save(path + "/" + FILENAME.IRREGULAR_DIC)
        self.grammar.save(path + "/" + FILENAME.GRAMMAR)

    def load(self, path):
        self.word_dic.load(path + "/" + FILENAME.WORD_DIC)
        self.irr_dic.load(path + "/" + FILENAME.IRREGULAR_DIC)
        self.grammar.load(path + "/" + FILENAME.GRAMMAR)

    def build_path(self, corpora_path, suffix=None):
        _filenames = [f.name for f in os.scandir(corpora_path) if f.is_file()]
        for _filename in _filenames:
            _abs_filename = corpora_path + "/" + _filename
            if suffix is None:
                print(_abs_filename)
                self.build(_abs_filename)
            else:
                if _filename.endswith(suffix):
                    print(_abs_filename)
                    self.build(_abs_filename)
        print("before pruning")
        print(f"dic size = {len(self.word_dic.get_dict())}")
        print(f"irr dic size = {len(self.irr_dic.get_dict())}")
        print(f"grammar size = {len(self.grammar.get_grammar())}")
        self._pruning()
        print("after pruning")
        print(f"dic size = {len(self.word_dic.get_dict())}")
        print(f"irr dic size = {len(self.irr_dic.get_dict())}")
        print(f"grammar size = {len(self.grammar.get_grammar())}")

    def build(self, _filename):
        with open(_filename, 'r') as f:
            for line in f.readlines():
                line = re.sub("[ ]+", " ", line).strip()
                if len(line) == 0:
                    continue
                pa_pair = self.corpus_parser.parse(line)
                if pa_pair is None:
                    continue
                self._append_word_dic(pa_pair.get_answer_list())
                self._append_irr_dic(pa_pair)
                self._append_grammar(pa_pair.get_answer_list())

    def _append_word_dic(self, answer_list):
        for answer in answer_list:
            # todo : KOMORAN 에는 뭔가 예외처리가 있는 것으로 보이는데 그 부분은 구현하지 않았음
            _word = answer[0]
            _pos = answer[1]
            self.word_dic.append(_word, _pos)

    def _append_irr_dic(self, problem_answer):
        if self._is_irregular(problem_answer.get_problem(), problem_answer.get_answer_list()):
            _irr_rules = self.irregular_parser.parse(KoreanUnitParser.parse(problem_answer.get_problem()),
                                                     [(KoreanUnitParser.parse(_word), _pos) for _word, _pos in
                                                      problem_answer.get_answer_list()])
            for _irr_rule in _irr_rules:
                _irr = _irr_rule[0]
                _rule = _irr_rule[1]
                if len(_rule.strip()) == 0:
                    continue
                # 불규칙 대상에 자소가 하나의 음절로 포함된 경우 skip
                # todo : KOMORAN에서는 불규칙 예외에 대한 처리를 하지만 그 부분은 구현하지 않았음
                _has_jaso_problem = False
                reunion_irr_syllable = KoreanUnitParser.combine(_irr)
                reunion_rule_syllable = KoreanUnitParser.combine(_rule)
                for _letter in reunion_irr_syllable:
                    if is_jamo(_letter):
                        _has_jaso_problem = True
                        break
                if _has_jaso_problem:
                    continue
                self.irr_dic.append(reunion_irr_syllable, reunion_rule_syllable)

    def _is_irregular(self, problem, answer_list):
        _answer_str = ""
        for answer in answer_list:
            _word = answer[0]
            _answer_str += _word
        problem_unit = self.unit_parser.parse(problem)
        answer_unit = self.unit_parser.parse(_answer_str)
        # todo : KOMORAN 에서는 한국어만 추출해서 비교하지만 그 부분은 생략하였음
        return problem_unit != answer_unit

    def _append_grammar(self, answer_list):
        _prev_pos = SYMBOL.BOE
        for answer in answer_list:
            # todo : KOMORAN에서는 correctGrammar라는 별도의 문법을 입력 받은 뒤에 처리하는 로직이 있으나 구현하지 않음
            _current_pos = answer[1]
            self.grammar.append(_prev_pos, _current_pos)
            _prev_pos = answer[1]
        _end_pos = SYMBOL.EOE
        self.grammar.append(_prev_pos, _end_pos)

    def _pruning(self):
        # dic pruning
        pruned_dic, pruned_words = self._pruning_dic(self.word_dic.get_dict(), freq_threshold=2)
        self.word_dic = Dictionary(pruned_dic)
        with open('excluded_nouns.txt', 'w') as f:
            for word in pruned_words:
                f.write(word + "\n")
        # grammar pruning
        self.grammar = Grammar(self._pruning_dic(self.grammar.get_grammar())[0])
        # irregular dic pruning
        self.irr_dic = Dictionary(self._pruning_dic(self.irr_dic.get_dict())[0])

    @staticmethod
    def _pruning_dic(dic, freq_threshold=5):
        _pruned_dic = {}
        _pruned_words = []
        for _word, _pos_freq_dic in dic.items():
            _pruned_pos_freq_dic = {}
            for _pos, _freq in _pos_freq_dic.items():
                if _freq <= freq_threshold:
                    if _pos == 'NNG' or _pos == 'NNP':
                        _pruned_words.append(_word)
                    continue
                _pruned_pos_freq_dic[_pos] = _freq
            if len(_pruned_pos_freq_dic) != 0:
                _pruned_dic[_word] = _pruned_pos_freq_dic
        return _pruned_dic, _pruned_words
