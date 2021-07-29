class Dictionary:
    def __init__(self, init_dic=None):
        if init_dic is None:
            init_dic = {}
        self._dictionary = init_dic

    def load(self, filename):
        self._dictionary = {}
        with open(filename, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                _tokens = line.split('\t')
                _key = _tokens[0]
                _value_freq_dic = {}
                for _token_idx in range(1, len(_tokens)):
                    _token = _tokens[_token_idx]
                    _separator_idx = _token.rindex(':')
                    _value = _token[0:_separator_idx]
                    _freq = int(_token[_separator_idx + 1:])
                    _value_freq_dic[_value] = _freq
                self._dictionary[_key] = _value_freq_dic

    def save(self, filename):
        with open(filename, 'w') as f:
            for _key, _value_freq_dic in self._dictionary.items():
                f.write(
                    _key + "\t" + "\t".join([f"{_value}:{_freq}" for _value, _freq in _value_freq_dic.items()]) + "\n")

    def append(self, key, value, freq=1):
        _value_freq_dic = self._dictionary.get(key)
        if _value_freq_dic is None:
            _value_freq_dic = {}

        _freq = _value_freq_dic.get(value)
        if _freq is None:
            _freq = 0
        _freq += freq
        _value_freq_dic[value] = _freq
        self._dictionary[key] = _value_freq_dic

    def get_pos_freq_dict(self, key):
        return self._dictionary.get(key)

    def get_dict(self):
        return self._dictionary

    def print(self):
        print(self._dictionary)

    def __repr__(self):
        return f'Dictionary: {self._dictionary}'
