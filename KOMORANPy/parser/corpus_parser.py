import sys

from ..parser.problem_answer_info import ProblemAnswerInfo


class CorpusParser:

    def __init__(self):
        pass

    def parse(self, line):
        _problem_answers = line.split("\t")
        if len(_problem_answers) != 2:
            sys.stderr.write("Corpus format error. (CorpusParser.parse): " + line + "\n")
            sys.exit(-1)

        self._problem = _problem_answers[0]
        self._answer = _problem_answers[1]
        self._answer_list = []
        if self._parser_answer(self._answer):
            return ProblemAnswerInfo(self._problem, self._answer, self._answer_list)
        else:
            return None

    def _parser_answer(self, answer_texts):
        # todo : 현재는 multi word를 하나의 단어로 인식하는 기능은 제외 시킴
        _tokens = answer_texts.split(' ')
        for _token in _tokens:
            _split_idx = _token.rindex('/')
            _word = _token[0:_split_idx].strip()
            _pos = _token[_split_idx + 1:].strip()
            if len(_word) == 0 or len(_pos) == 0 or _pos == 'NA':
                sys.stderr.write("Corpus format error (CorpusParser._parser_answer): " + answer_texts + "\n")
                return False
            self._answer_list.append((_word, _pos))
        return True

#
# with open('/Users/shinjunsoo/shineware/data/komoran_training_data/현대문어_형태분석_말뭉치.refine.txt') as f:
#     corpus_parser = CorpusParser()
#     for line in f.readlines():
#         line = line.strip()
#         if len(line) == 0:
#             continue
