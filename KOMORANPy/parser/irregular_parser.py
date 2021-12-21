from ..parser.korean_unit_parser import is_korean


class IrregularParser:
    def __init__(self):
        self._answer_begin_idx = -1
        self._problem_begin_idx = -1
        self._answer_end_idx = -1
        self._problem_end_idx = -1

    def parse(self, problem, answer_list):
        self.__init__()
        self._set_begin_idx(problem, answer_list)
        self._set_end_idx(problem, answer_list)
        return self._get_irregular_rules(problem, answer_list)

    def _set_begin_idx(self, problem, answer_list):
        # left to right retrieval
        _ptr = 0
        for _idx, _answer in enumerate(answer_list):
            _word, _pos = _answer
            if _ptr + len(_word) > len(problem):
                self._answer_begin_idx = _idx
                self._problem_begin_idx = _ptr
                break

            _problem_sub_token = problem[_ptr:_ptr + len(_word)]
            if _word != _problem_sub_token:
                self._answer_begin_idx = _idx
                self._problem_begin_idx = _ptr
                break
            _ptr += len(_word)

    def _set_end_idx(self, problem, answer_list):
        # right to left retrieval
        _ptr = len(problem)
        for _idx, _answer in reversed(list(enumerate(answer_list))):
            _word, _pos = _answer
            if _ptr - len(_word) < 0:
                self._answer_end_idx = _idx
                self._problem_end_idx = _ptr
                break

            _problem_sub_token = problem[_ptr - len(_word):_ptr]
            if _word != _problem_sub_token:
                self._answer_end_idx = _idx
                self._problem_end_idx = _ptr
                break

            _ptr = _ptr - len(_word)

    def _get_irregular_rules(self, problem, answer_list):
        _irr_rules = []
        if not self._is_clean_rule(problem, answer_list):
            return _irr_rules
        # 불규칙 시작지점과 끝지점이 cross 되는 경우
        # 알리가 -> 알 + ㄹ + 리가
        # 시작지점 ( left to right ) = 4 ( ㅣㄱㅏ )
        # 끝 지점 ( right to left ) = 2 ( ㅇㅏ )
        if self._problem_begin_idx > self._problem_end_idx:
            # 시작 지점 처리
            _irr_problem = problem[0:self._problem_end_idx].strip()
            if len(_irr_problem) == 0 or self._answer_end_idx == 0:
                _irr_rule = self._expand_irregular_rule(problem, answer_list, 0, self._problem_end_idx, 0,
                                                        self._answer_end_idx)
            else:
                _irr_rule = self._build_irregular_rule(_irr_problem, answer_list, 0, self._answer_end_idx)
            _irr_rules.append(_irr_rule)

            # 끝 지점 처리
            _irr_problem = problem[self._problem_begin_idx:].strip()
            if len(_irr_problem) == 0 or self._answer_begin_idx == len(answer_list) - 1:
                if self._answer_begin_idx - 1 >= len(answer_list):
                    print(f"{problem} -> {answer_list}")
                    print(answer_list[self._answer_begin_idx - 1])
                _irr_rule = self._expand_irregular_rule(problem, answer_list, self._problem_begin_idx, len(problem),
                                                        self._answer_begin_idx, len(answer_list) - 1)
            else:
                _irr_rule = self._build_irregular_rule(_irr_problem, answer_list, self._answer_begin_idx,
                                                       len(answer_list) - 1)
            _irr_rules.append(_irr_rule)
        # 축약인 경우
        # 너라고 -> 너 + 이 + 라고
        # 불규칙 패턴의 형태소룰 앞, 뒤로 하나씩 확장
        # "null" -> "이"의 패턴을 "너라고 -> 너 + 이 + 라고"로 확장
        elif self._problem_begin_idx == self._problem_end_idx:
            _irr_rule = self._expand_irregular_rule(problem, answer_list, self._problem_begin_idx,
                                                    self._problem_end_idx, self._answer_begin_idx, self._answer_end_idx)
            _irr_rules.append(_irr_rule)
        else:
            _irr_problem = problem[self._problem_begin_idx:self._problem_end_idx].strip()
            # 탈락인 경우
            # 어떠냐 -> 어떻 + 냐
            # 어떠 -> null 인 경우 단일 형태소 그대로 사용 ( 어떠 -> 어떻 )
            if self._answer_begin_idx == self._answer_end_idx:
                _extract_length = self._problem_end_idx - self._problem_begin_idx
                if _extract_length < 4:
                    _irr_rule = self._expand_irregular_rule(problem, answer_list, self._problem_begin_idx,
                                                            self._problem_end_idx, self._answer_begin_idx,
                                                            self._answer_end_idx)
                else:
                    _irr_rule = self._build_irregular_rule(_irr_problem, answer_list, self._answer_begin_idx,
                                                           self._answer_end_idx)
            else:
                _irr_rule = self._build_irregular_rule(_irr_problem, answer_list, self._answer_begin_idx,
                                                       self._answer_end_idx)
            _irr_rules.append(_irr_rule)

        return _irr_rules

    def _is_clean_rule(self, problem, answer_list):

        if self._answer_begin_idx == -1 or self._answer_end_idx == -1:
            return False

        if answer_list[self._answer_end_idx] == "VCP":
            return False

        i = self._answer_begin_idx
        while i < self._answer_end_idx+1:
            _pos = answer_list[i][1]
            if _pos == "NNP" or _pos == "NNG" or _pos.startswith("JK"):
                return False
            i += 1

        for _letter in problem:
            if not is_korean(_letter):
                return False

        return True

    @staticmethod
    def _expand_irregular_rule(problem, answer_list, problem_begin_idx, problem_end_idx, answer_begin_idx,
                               answer_end_idx):
        _center_convert_rule = ""
        for i in range(answer_begin_idx, answer_end_idx + 1):
            _word = answer_list[i][0]
            _pos = answer_list[i][1]
            _center_convert_rule += f"{_word}/{_pos} "

        _prev_convert_rule = ""
        _next_convert_rule = ""

        _tmp_problem_begin_idx = problem_begin_idx
        _tmp_problem_end_idx = problem_end_idx

        if answer_begin_idx != 0:
            _word = answer_list[answer_begin_idx - 1][0]
            _pos = answer_list[answer_begin_idx - 1][1]
            _prev_convert_rule += f"{_word}/{_pos} "
            _tmp_problem_begin_idx = problem_begin_idx - len(_word)

        if answer_end_idx + 1 != len(answer_list):
            _word = answer_list[answer_end_idx + 1][0]
            _pos = answer_list[answer_end_idx + 1][1]
            _next_convert_rule += f"{_word}/{_pos} "
            _tmp_problem_end_idx = problem_end_idx + len(_word)

        _convert_rule = _prev_convert_rule + _center_convert_rule + _next_convert_rule.strip()
        _irr_problem = problem[_tmp_problem_begin_idx:_tmp_problem_end_idx]
        return _irr_problem, _convert_rule.strip()

    @staticmethod
    def _build_irregular_rule(problem, answer_list, answer_begin_idx, answer_end_idx):
        _convert_rule = ""
        for i in range(answer_begin_idx, answer_end_idx + 1):
            _word = answer_list[i][0]
            _pos = answer_list[i][1]
            _convert_rule += f"{_word}/{_pos} "
        return problem, _convert_rule.strip()