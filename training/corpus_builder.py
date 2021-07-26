import os
import re
import shutil

from common.dictionary import Dictionary
from common.grammar import Grammar
from constant import FILENAME
from parser.corpus_parser import CorpusParser
from parser.irregular_parser import IrregularParser
from parser.korean_unit_parser import KoreanUnitParser


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
                # self._append_grammar(pa_pair.get_answer_list())

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
                # todo : here to go! KOMORAN에서는 불규칙 예외에 대한 처리를 하지만 그 부분은 구현하지 않았음
                _has_jaso_problem = False
                # print(_irr)
                # print(_rule)


    def _is_irregular(self, problem, answer_list):
        _answer_str = ""
        for answer in answer_list:
            _word = answer[0]
            _answer_str += _word
        problem_unit = self.unit_parser.parse(problem)
        answer_unit = self.unit_parser.parse(_answer_str)
        # todo : KOMORAN 에서는 한국어만 추출해서 비교하지만 그 부분은 생략하였음
        return problem_unit != answer_unit


corpus_builder = CorpusBuilder()
corpus_builder.build_path("/Users/shinjunsoo/shineware/data/komoran_training_data", "refine.txt")
corpus_builder.save("corpus_build")
