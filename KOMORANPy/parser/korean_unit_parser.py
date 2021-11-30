import re
from bisect import bisect_left
from enum import Enum

chosung_list = [0x3131, 0x3132, 0x3134, 0x3137, 0x3138,
                0x3139, 0x3141, 0x3142, 0x3143, 0x3145, 0x3146, 0x3147, 0x3148,
                0x3149, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e]
jungsung_list = [0x314f, 0x3150, 0x3151, 0x3152, 0x3153,
                 0x3154, 0x3155, 0x3156, 0x3157, 0x3158, 0x3159, 0x315a, 0x315b,
                 0x315c, 0x315d, 0x315e, 0x315f, 0x3160, 0x3161, 0x3162, 0x3163]
jongsung_list = [0x0000, 0x3131, 0x3132, 0x3133, 0x3134,
                 0x3135, 0x3136, 0x3137, 0x3139, 0x313a, 0x313b, 0x313c, 0x313d,
                 0x313e, 0x313f, 0x3140, 0x3141, 0x3142, 0x3144, 0x3145, 0x3146,
                 0x3147, 0x3148, 0x314a, 0x314b, 0x314c, 0x314d, 0x314e]


class UnitType(Enum):
    CHOSUNG = 1
    JUNGSUNG = 2
    JONGSUNG = 3
    OTHER = 4


def binary_search(collection, element):
    _idx = bisect_left(collection, element)
    if _idx == len(collection) or collection[_idx] != element:
        return -1
    return _idx


class KoreanUnitParser:

    @staticmethod
    def parse_with_type(text):
        _result = []
        for ch in text:
            hex_value = ord(ch)
            # 음절 영역
            if 0xAC00 <= hex_value <= 0xD7AF:
                _cho_idx = _jung_idx = _jong_idx = _tmp_idx = 0
                _tmp_idx = int(hex_value - 0xAC00)
                _cho_idx = int(_tmp_idx / (21 * 28))
                _tmp_idx = int(_tmp_idx % (21 * 28))
                _jung_idx = int(_tmp_idx / 28)
                _jong_idx = int(_tmp_idx % 28)
                _result.append((chr(chosung_list[_cho_idx]), chosung_list[_cho_idx], UnitType.CHOSUNG))
                _result.append((chr(jungsung_list[_jung_idx]), jungsung_list[_jung_idx], UnitType.JUNGSUNG))
                if _jong_idx != 0:
                    _result.append((chr(jongsung_list[_jong_idx]), jongsung_list[_jong_idx], UnitType.JONGSUNG))

            else:
                _result.append((ch, None, UnitType.OTHER))
        return _result

    @staticmethod
    def parse(text):
        _result = []
        for ch in text:
            hex_value = ord(ch)
            # 음절 영역
            if 0xAC00 <= hex_value <= 0xD7AF:
                _cho_idx = _jung_idx = _jong_idx = _tmp_idx = 0
                _tmp_idx = int(hex_value - 0xAC00)
                _cho_idx = int(_tmp_idx / (21 * 28))
                _tmp_idx = int(_tmp_idx % (21 * 28))
                _jung_idx = int(_tmp_idx / 28)
                _jong_idx = int(_tmp_idx % 28)
                _result.append(chr(chosung_list[_cho_idx]))
                _result.append(chr(jungsung_list[_jung_idx]))
                if _jong_idx != 0:
                    _result.append(chr(jongsung_list[_jong_idx]))
            else:
                _result.append(ch)
        return "".join(_result)

    @staticmethod
    def combine_with_type(jaso_with_types):
        _chosung = _jungsung = _jongsung = 0
        _has_buffer = False

        _result = ""

        for _jaso, _hex, _type in jaso_with_types:
            if _type == UnitType.CHOSUNG:
                if _has_buffer:
                    _result += chr(0xac00 + _chosung * 588 + _jungsung * 28 + _jongsung)
                    _jungsung = _jongsung = 0
                _chosung = binary_search(chosung_list, _hex)
                _has_buffer = True
            elif _type == UnitType.JUNGSUNG:
                _jungsung = binary_search(jungsung_list, _hex)
                _has_buffer = True
            elif _type == UnitType.JONGSUNG:
                _jongsung = binary_search(jongsung_list, _hex)
                _has_buffer = True
            else:
                if _has_buffer:
                    _result += chr(0xac00 + _chosung * 588 + _jungsung * 28 + _jongsung)
                    _chosung = _jungsung = _jongsung = 0
                _result += _jaso
                _has_buffer = False

        if _has_buffer:
            _result += chr(0xac00 + _chosung * 588 + _jungsung * 28 + _jongsung)
        return _result

    @staticmethod
    def combine(jaso_text):
        _idx = 1
        _prev_idx = 0
        _result = ""
        while _idx < len(jaso_text):
            _hex = ord(jaso_text[_idx])
            _jungsung = binary_search(jungsung_list, _hex)
            if _jungsung >= 0:
                _hex = ord(jaso_text[_idx - 1])
                _chosung = binary_search(chosung_list, _hex)
                if _chosung < 0:
                    _idx += 1
                    continue
                _result += jaso_text[_prev_idx:_idx - 1]

                _jongsung = 0
                if _idx + 1 < len(jaso_text):
                    _hex = ord(jaso_text[_idx + 1])
                    _jongsung = binary_search(jongsung_list, _hex)
                if _idx + 2 < len(jaso_text) and binary_search(jungsung_list, ord(jaso_text[_idx + 2])) >= 0:
                    _jongsung = 0
                # 종성이 없는 경우
                if _jongsung < 0:
                    _jongsung = 0
                _result += chr(0xac00 + _chosung * 588 + _jungsung * 28 + _jongsung)
                if _jongsung > 0:
                    _idx += 1
                _prev_idx = _idx + 1
            _idx += 1
        if _prev_idx < len(jaso_text):
            _result += jaso_text[_prev_idx:]

        return _result


def is_korean(letter):
    return re.search('[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]+', letter) is not None


def is_jamo(letter):
    _hex = ord(letter)
    return 0x3131 <= _hex <= 0x318E
