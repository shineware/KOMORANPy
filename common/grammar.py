class Grammar:
    def __init__(self, init_grammar=None):
        if init_grammar is None:
            init_grammar = {}
        self._grammar = init_grammar

    def load(self, filename):
        self._grammar = {}
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                _tokens = line.split('\t')
                _prev_pos = _tokens[0]
                _cur_pos_freq_dic = {}
                _cur_pos_tokens = _tokens[1].split(',')
                for _token_idx in range(0, len(_cur_pos_tokens)):
                    _token = _cur_pos_tokens[_token_idx]
                    _separator_idx = _token.rindex(':')
                    _cur_pos = _token[0:_separator_idx]
                    _freq = int(_token[_separator_idx + 1:])
                    _cur_pos_freq_dic[_cur_pos] = _freq
                self._grammar[_prev_pos] = _cur_pos_freq_dic

    def save(self, filename):
        with open(filename, 'w') as f:
            for _prev_pos, _cur_pos_freq_dic in self._grammar.items():
                f.write(
                    _prev_pos + "\t" + ",".join(
                        [f"{_cur_pos}:{_freq}" for _cur_pos, _freq in _cur_pos_freq_dic.items()]) + "\n")

    def append(self, prev_pos, cur_pos, freq=1):
        _cur_pos_freq_dic = self._grammar.get(prev_pos)
        if _cur_pos_freq_dic is None:
            _cur_pos_freq_dic = {}

        _freq = _cur_pos_freq_dic.get(cur_pos)
        if _freq is None:
            _freq = 0
        _freq += freq
        _cur_pos_freq_dic[cur_pos] = _freq
        self._grammar[prev_pos] = _cur_pos_freq_dic

    def print(self):
        print(self._grammar)

    def __repr__(self):
        return f'Grammar: {self._grammar}'

    def has(self, prev_pos, cur_pos):
        _cur_pos_freq_dict = self._grammar.get(prev_pos)
        if _cur_pos_freq_dict is None:
            return False
        else:
            _freq = _cur_pos_freq_dict.get(cur_pos)
            return _freq is not None

    def get_grammar(self):
        return self._grammar
