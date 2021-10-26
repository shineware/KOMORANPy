class StringUtil:

    @staticmethod
    def is_basic_latic(hex_code):
        return 0x0000 <= hex_code <= 0x007F

    @staticmethod
    def is_num(hex_code):
        return 0x0030 <= hex_code <= 0x0039

    @staticmethod
    def is_english(hex_code):
        return 0x0041 <= hex_code <= 0x005A or 0x0061 <= hex_code <= 0x007A

    @staticmethod
    def is_korean(hex_code):
        # HANGUL SYLLABLES
        # or HANGUL COMPATIBILITY JAMO
        # or HANGUL JAMO
        return 0xAC00 <= hex_code <= 0xD7A3 \
               or 0x3131 <= hex_code <= 0x318E \
               or 0x1100 <= hex_code <= 0x11F9

    @staticmethod
    def is_japanese(hex_code):
        # KATAKANA
        # or KATAKANA PHONETIC EXTENSIONS
        # or HIRAGANA
        return 0x30A0 <= hex_code <= 0x30FF \
               or 0x31F0 <= hex_code <= 0x31FF \
               or 0x3041 <= hex_code <= 0x309F

    @staticmethod
    def is_chinese(hex_code):
        # CJK_COMPATIBILITY
        # or CJK_UNIFIED_IDEOGRAPHS
        # or CJK_UNIFIED_IDEOGRAPHS_EXTENSION_A
        # or CJK_UNIFIED_IDEOGRAPHS_EXTENSION_B
        # or CJK_COMPATIBILITY_IDEOGRAPHS
        return 0x3300 <= hex_code <= 0x33FE \
               or 0x4E00 <= hex_code <= 0x9FFF \
               or 0x3400 <= hex_code <= 0x4DB5 \
               or 0x20000 <= hex_code <= 0x2A6DF \
               or 0xF900 <= hex_code <= 0xFACF
