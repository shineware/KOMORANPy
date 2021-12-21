import math

from ..common.irregular.irregular_trie import IrregularTrie
from ..constant import SYMBOL, FILENAME
from ..parser.korean_unit_parser import KoreanUnitParser
from ..training.model.observation import Observation
from ..training.model.pos_table import PosTable
from ..training.model.transition import Transition
from ..utils.string_util import StringUtil


class Model:
    def __init__(self, model_path):
        self.transition = Transition(0)
        self.observation = Observation()
        self.pos_table = PosTable()
        self.irr_trie = IrregularTrie()
        self.transition.load(model_path + "/" + FILENAME.TRANSITION)
        self.observation.load(model_path + "/" + FILENAME.OBSERVATION)
        self.pos_table.load(model_path + "/" + FILENAME.POS_TABLE)
        self.irr_trie.load(model_path + "/" + FILENAME.IRREGULAR_MODEL)
        self.observation.get_dictionary().build_fail_link()
        self.irr_trie.get_dictionary().build_fail_link()


class LatticeNode:
    def __init__(self, begin_idx, end_idx, word, pos, pos_id, score):
        self.__begin_idx = begin_idx
        self.__end_idx = end_idx
        self.__word = word
        self.__pos = pos
        self.__pos_id = pos_id
        self.__score = score
        self.__prev_node_idx = -1
        self.__is_irregular = False

    def __repr__(self):
        return f"""(begin_idx={self.__begin_idx}, end_idx={self.end_idx}, word={self.word}, pos={self.pos}, pos_id={self.pos_id}, score={self.score}, prev_node_idx={self.prev_node_idx}, is_irregular={self.__is_irregular})"""

    @property
    def begin_idx(self):
        return self.__begin_idx

    @begin_idx.setter
    def begin_idx(self, value):
        self.__begin_idx = value

    @property
    def end_idx(self):
        return self.__end_idx

    @end_idx.setter
    def end_idx(self, value):
        self.__end_idx = value

    @property
    def word(self):
        return self.__word

    @word.setter
    def word(self, value):
        self.__word = value

    @property
    def pos(self):
        return self.__pos

    @pos.setter
    def pos(self, value):
        self.pos = value

    @property
    def pos_id(self):
        return self.__pos_id

    @pos_id.setter
    def pos_id(self, value):
        self.__pos_id = value

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, value):
        self.__score = value

    @property
    def prev_node_idx(self):
        return self.__prev_node_idx

    @prev_node_idx.setter
    def prev_node_idx(self, value):
        self.__prev_node_idx = value

    @property
    def is_irregular(self):
        return self.__is_irregular

    @is_irregular.setter
    def is_irregular(self, value):
        self.__is_irregular = value


class Lattice:
    def __init__(self, model, user_dic):
        self.model = model
        self.user_dic = user_dic
        self.init_node()
        self.make_new_contexts()

    """
    word_pos_list = [('ㄱㅗ', 15), (',', 5)]
    """

    def attach_info_to_word_pos_list(self, word_pos_list):
        results = []
        for word, pos_id in word_pos_list:
            # return get_value 의 형태는 이런 식임 [('EC', 15, -2.107718373555622), ('EF', 19, -3.972572410841921)]
            # todo : for 문을 돌면서 list에서 pos에 해당하는 score 값을 찾아야 하기 때문에 이 부분은 추후 개선의 여지가 필요함 ( 바로 찾을 수 있는 방법.. )
            # observation score 가져오기
            for _pos, _pos_id, _score in self.model.observation.get_dictionary().get_value(word):
                if pos_id == _pos_id:
                    results.append((word, _pos, pos_id, _score))
                    break
        return results

    def make_new_contexts(self):
        self.observation_context = self.model.observation.get_dictionary().new_find_context()
        self.irregular_context = self.model.irr_trie.get_dictionary().new_find_context()
        if self.user_dic is not None:
            self.user_dic_context = self.user_dic.get_dictionary().new_find_context()

    def init_node(self):
        self.lattice = {}
        self.irr_idx = 0
        lattice_nodes = [LatticeNode(-1, 0, SYMBOL.BOE, SYMBOL.BOE, self.model.pos_table.get_id(SYMBOL.BOE), 0.0)]
        self.lattice[0] = lattice_nodes

    def get_observation(self, jaso_unit):
        return self.model.observation.get_dictionary().get(jaso_unit, self.observation_context)

    def get_irregular_nodes(self, jaso_unit):
        return self.model.irr_trie.get_dictionary().get(jaso_unit, self.irregular_context)

    def get_user_dic(self, jaso_unit):
        if self.user_dic is not None:
            return self.user_dic.get_dictionary().get(jaso_unit, self.user_dic_context)
        return None

    def put(self, begin_idx, end_idx, word, pos, pos_id, observation_score, is_irregular=False):
        prev_lattice_nodes = self.lattice.get(begin_idx)
        if prev_lattice_nodes is None:
            return False
        else:
            max_lattice_node = self.get_max_transition_node(prev_lattice_nodes, begin_idx, end_idx, word, pos, pos_id,
                                                            observation_score)
            if max_lattice_node is not None:
                max_lattice_node.is_irregular = is_irregular
                self.append_node(max_lattice_node)
                return True
        return False

    def get_max_transition_node(self, prev_lattice_nodes, begin_idx, end_idx, word, pos, pos_id, observation_score):
        prev_max_node = None
        max_score = -math.inf
        lattice_node_idx = -1
        prev_lattice_node_idx = -1
        for prev_lattice_node in prev_lattice_nodes:
            lattice_node_idx += 1
            # 불규칙 확장인 경우
            # todo : KOMORAN에서는 pos_id == -1 인 경우(불규칙 확장. 일반 불규칙이 아님)에 continue 했으나 해당 로직이 왜 필요한지는 의문...
            # 일단 KOMORAN 의 불규칙 확장 알고리즘 중 자식 노드 유무에 따라 탐색 후보로 등록하는 부분이 제외되었기 때문에 아래 continue 부분은 실제로 걸리는 케이스가 없음
            # if prev_lattice_node.is_irregular:
            if prev_lattice_node.pos_id == -1:
                continue

            prev_pos_id = -1
            prev_word = ''
            if prev_lattice_node.pos == SYMBOL.EOE:
                prev_pos_id = self.model.pos_table.get_id(SYMBOL.BOE)
                prev_word = SYMBOL.BOE
            else:
                prev_pos_id = prev_lattice_node.pos_id
                prev_word = prev_lattice_node.word

            # 전이확률 값
            transition_score = self.model.transition.get(prev_pos_id, pos_id)
            if transition_score is None:
                continue

            # todo : 결합 규칙 체크 부분은 생략 됨

            prev_observation_score = prev_lattice_node.score
            if max_score < transition_score + prev_observation_score:
                max_score = transition_score + prev_observation_score
                prev_max_node = prev_lattice_node
                prev_lattice_node_idx = lattice_node_idx
        if prev_max_node is not None:
            lattice_node = LatticeNode(begin_idx, end_idx, word, pos, pos_id, max_score + observation_score)
            lattice_node.prev_node_idx = prev_lattice_node_idx
            return lattice_node

        return None

    def append_node(self, lattice_node):
        lattice_nodes = self.lattice.get(lattice_node.end_idx)
        if lattice_nodes is None:
            lattice_nodes = []
        lattice_nodes.append(lattice_node)
        self.lattice[lattice_node.end_idx] = lattice_nodes
        return len(lattice_nodes) - 1


class ChunkLetter:
    def __init__(self):
        self.prev_pos = ""
        self.prev_word = ""
        self.prev_begin_idx = 0

    def get_prev_pos(self):
        return self.prev_pos

    def get_prev_word(self):
        return self.prev_word

    def get_prev_begin_idx(self):
        return self.prev_begin_idx

    def set_prev_pos(self, prev_pos):
        self.prev_pos = prev_pos

    def set_prev_word(self, prev_word):
        self.prev_word = prev_word

    def set_prev_begin_idx(self, prev_begin_idx):
        self.prev_begin_idx = prev_begin_idx


class Komoran:
    def __init__(self, model_path):
        print(f'load model : {model_path}')
        self.model = Model(model_path)
        self.unit_parser = KoreanUnitParser()
        self.user_dic = None
        self.fwd = None
        print(f'load done')

    def set_user_dic(self, user_dic_path):
        self.user_dic = Observation()
        with open(user_dic_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                tokens = line.split('\t', 1)
                if len(tokens) == 1:
                    word = tokens[0]
                    pos = "NNP"
                else:
                    word = tokens[0]
                    pos = tokens[1]
                self.user_dic.put(word, pos, self.model.pos_table.get_id(pos), 0.0)
        self.user_dic.get_dictionary().build_fail_link()

    def set_fwd(self, fwd_path):
        with open(fwd_path, 'r') as f:
            self.fwd = {}
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                tokens = line.split('\t')
                if len(tokens) != 2:
                    continue
                target_word = tokens[0]
                analyzed_results = []
                for analyzed_result in tokens[1].split(' '):
                    word, pos = analyzed_result.rsplit('/', 1)
                    analyzed_results.append((word, pos))
                self.fwd[self.unit_parser.parse(target_word)] = analyzed_results

    def analyze(self, sentence):
        lattice = Lattice(self.model, self.user_dic)
        jaso_units = self.unit_parser.parse(sentence)
        extra_lattice_idx = -1
        whitespace_idx = 0
        idx = 0
        chunk_letter = ChunkLetter()
        while idx < len(jaso_units):
            jaso_unit = jaso_units[idx]
            # todo : here we go! 기호 처리 결과 확인 및 연속 기호 처리
            # 기분석 사전 적용
            next_whitespace_idx, extra_lattice_idx = self.lookup_fwd(lattice, jaso_units, idx, extra_lattice_idx)
            if next_whitespace_idx != -1:
                idx = next_whitespace_idx - 1
                continue
            # 공백 문자인 경우에
            if jaso_unit == ' ':
                self.consume_remain_chunk_letter(lattice, idx, chunk_letter)
                self.bridging_lattice(lattice, whitespace_idx, idx, jaso_units)
                whitespace_idx = idx + 1

            # 사용자 사전 적용
            self.user_dic_parsing(lattice, jaso_unit, idx)
            # 기호 파싱
            self.symbol_parsing(lattice, jaso_unit, idx)
            # 연속 문자 (숫자, 영어, 한자 등)
            self.chunk_letter_parsing(lattice, jaso_unit, idx, chunk_letter)

            # 단어 파싱
            self.regular_parsing(lattice, jaso_unit, idx)
            extra_lattice_idx = self.irregular_parsing(lattice, jaso_unit, idx, extra_lattice_idx)
            self.irregular_extends(lattice, jaso_unit, idx)
            idx += 1

        last_idx = len(jaso_units)
        # 단어 끝에 어절 마지막 노드 추가
        self.consume_remain_chunk_letter(lattice, last_idx, chunk_letter)
        self.bridging_lattice(lattice, whitespace_idx, last_idx, jaso_units)
        last_idx += 1

        # for i in range(irr_idx, last_idx + 1):
        #     lattice_nodes = lattice.lattice.get(i)
        #     if lattice_nodes is None:
        #         continue
        #     print(f'{i} :')
        #     for lattice_node in lattice_nodes:
        #         print(f'\t{lattice_node}')

        # get max transitions
        result = []
        end_node = lattice.lattice.get(last_idx)[0]
        begin_idx = end_node.begin_idx
        prev_node_idx = end_node.prev_node_idx
        while True:
            node = lattice.lattice.get(begin_idx)[prev_node_idx]
            if node.word == SYMBOL.BOE:
                break
            word = node.word
            pos = node.pos
            result.append((word, pos))
            begin_idx = node.begin_idx
            prev_node_idx = node.prev_node_idx
        return reversed(result)
        # for word, pos in reversed(result):
        #     print(f"{word}/{pos}")

    def regular_parsing(self, lattice, jaso_unit, idx):
        # 아래와 같은 형태가 리턴 됨
        # {
        #   'ㅈㅏㅈ': [('VA', 20, -3.2449828635675546), ('VV', 14, -5.561212329330546)],
        #   'ㅈ': [('NNG', 2, -4.833270674064261)]
        # }
        word_with_pos_scores = lattice.get_observation(jaso_unit)
        if len(word_with_pos_scores) == 0:
            return
        for word, pos_scores in word_with_pos_scores.items():
            begin_idx = idx - len(word) + 1
            end_idx = idx + 1
            for pos, pos_id, observation_score in pos_scores:
                lattice.put(begin_idx, end_idx, word, pos, pos_id, observation_score)

    def irregular_parsing(self, lattice, jaso_unit, idx, extra_lattice_idx):
        # get_irregular_nodes 는 아래와 같은 형태가 리턴 됨
        # {
        #   'ㄱㅏ': [('ㅇㅓ', 15), ('ㄱㅏ', 27), ('ㅇㅏ', 15)]
        # }
        word_with_irr_nodes = lattice.get_irregular_nodes(jaso_unit)
        if len(word_with_irr_nodes) == 0:
            return extra_lattice_idx
        for word, irr_nodes in word_with_irr_nodes.items():
            # print(f"{word} -> {irr_nodes}")
            begin_idx = idx - len(word) + 1
            end_idx = idx + 1
            for irr_node in irr_nodes:
                word_with_pos_scores = lattice.attach_info_to_word_pos_list(irr_node.get_tokens())
                irregular_node_tokens_size = len(word_with_pos_scores)
                if irregular_node_tokens_size == 1:
                    _word, pos, pos_id, observation_score = word_with_pos_scores[0]
                    lattice.put(begin_idx, end_idx, _word, pos, pos_id, observation_score, True)
                    extra_lattice_idx -= 1
                else:
                    cnt = 0
                    for _word, pos, pos_id, observation_score in word_with_pos_scores:
                        if cnt == 0:
                            lattice.put(begin_idx, extra_lattice_idx, _word, pos, pos_id, observation_score, True)
                        elif cnt == len(word_with_pos_scores) - 1:
                            lattice.put(extra_lattice_idx + 1, end_idx, _word, pos, pos_id, observation_score, True)
                        else:
                            lattice.put(extra_lattice_idx + 1, extra_lattice_idx, _word, pos, pos_id, observation_score,
                                        True)
                        extra_lattice_idx -= 1
                        cnt += 1
        return extra_lattice_idx

    def irregular_extends(self, lattice, jaso_unit, idx):
        # todo : KOMORAN에서는 현재 자소를 뒤에 붙여서 확장하는 방법 외에 자식 노드가 있으면 계속 탐색 가능하게 처리하는 로직이 있음.
        # 그러나 해당 로직으로 인해서 어떠한 장점이 있는지 확인되지 않음. 그렇기 때문에 KOMORANPy 에서는 생략.
        prev_lattice_nodes = lattice.lattice.get(idx)
        if prev_lattice_nodes is None:
            return
        for prev_lattice_node in prev_lattice_nodes:
            if prev_lattice_node.is_irregular:
                extended_word = prev_lattice_node.word + jaso_unit
                # get_value 리턴 형태 = [('EP', 29, -0.723657199450198), ('VV', 14, -13.721442706150867)]
                observation_values = self.model.observation.get_dictionary().get_value(extended_word)
                if observation_values is None:
                    continue
                for pos, pos_id, score in observation_values:
                    lattice.put(prev_lattice_node.begin_idx, idx + 1, extended_word, pos, pos_id, score)

    def lookup_fwd(self, lattice, jaso_unit, idx, extra_lattice_idx):
        if self.fwd is None:
            return -1, extra_lattice_idx
        if idx == 0 or jaso_unit[idx - 1] == ' ':
            word_end_idx = jaso_unit.find(' ', idx)
            word_end_idx = len(jaso_unit) if word_end_idx == -1 else word_end_idx
            target_word = jaso_unit[idx:word_end_idx]
            word_pos_pairs = self.fwd.get(target_word)
            if word_pos_pairs is None:
                return -1, extra_lattice_idx
            # put(self, begin_idx, end_idx, word, pos, pos_id, observation_score, is_irregular=False):
            length = len(word_pos_pairs)
            if length == 1:
                word, pos = word_pos_pairs[0]
                pos_id = self.model.pos_table.get_id(pos)
                lattice.put(begin_idx=idx, end_idx=word_end_idx, word=word, pos=pos, pos_id=pos_id,
                            observation_score=0.0)
            else:
                fwd_idx = 0
                for word, pos in word_pos_pairs:
                    pos_id = self.model.pos_table.get_id(pos)
                    if fwd_idx == 0:
                        lattice.put(begin_idx=idx, end_idx=extra_lattice_idx - 1, word=word, pos=pos, pos_id=pos_id,
                                    observation_score=0.0)
                    elif fwd_idx == length - 1:
                        lattice.put(begin_idx=extra_lattice_idx, end_idx=word_end_idx, word=word, pos=pos,
                                    pos_id=pos_id, observation_score=0.0)
                    else:
                        lattice.put(begin_idx=extra_lattice_idx, end_idx=extra_lattice_idx - 1, word=word, pos=pos,
                                    pos_id=pos_id, observation_score=0.0)
                    extra_lattice_idx -= 1
                    fwd_idx += 1
            return word_end_idx, extra_lattice_idx
        return -1, extra_lattice_idx

    def bridging_lattice(self, lattice, whitespace_idx, idx, jaso_units):
        end_node_inserted = lattice.put(idx, idx + 1, SYMBOL.EOE, SYMBOL.EOE, self.model.pos_table.get_id(SYMBOL.EOE),
                                        0.0)
        # 마지막 노드가 추가되지 않았다면 NA임
        if not end_node_inserted:
            na_word = jaso_units[whitespace_idx:idx]
            na_lattice_node = LatticeNode(whitespace_idx, idx, na_word, SYMBOL.NA,
                                          self.model.pos_table.get_id(SYMBOL.NA), -10000.0)
            na_lattice_node.prev_node_idx = 0
            na_node_idx = lattice.append_node(na_lattice_node)

            end_lattice_node = LatticeNode(idx, idx + 1, SYMBOL.EOE, SYMBOL.EOE,
                                           self.model.pos_table.get_id(SYMBOL.EOE), 0.0)
            end_lattice_node.prev_node_idx = na_node_idx
            lattice.append_node(end_lattice_node)

    def user_dic_parsing(self, lattice, jaso_unit, idx):
        # 아래와 같은 형태가 리턴 됨
        # {
        #   'ㅈㅏㅈ': [('VA', 20, -3.2449828635675546), ('VV', 14, -5.561212329330546)],
        #   'ㅈ': [('NNG', 2, -4.833270674064261)]
        # }
        word_with_pos_scores = lattice.get_user_dic(jaso_unit)
        if word_with_pos_scores is None or len(word_with_pos_scores) == 0:
            return
        for word, pos_scores in word_with_pos_scores.items():
            begin_idx = idx - len(word) + 1
            end_idx = idx + 1
            for pos, pos_id, observation_score in pos_scores:
                lattice.put(begin_idx, end_idx, word, pos, pos_id, observation_score)

    def symbol_parsing(self, lattice, jaso_unit, idx):
        hex_value = ord(jaso_unit)
        if StringUtil.is_num(hex_value):
            return
        elif StringUtil.is_basic_latic(hex_value):
            if StringUtil.is_english(hex_value) is False \
                    and hex_value != 0x20 \
                    and self.model.observation.ahocorasick.get_value(jaso_unit) is None:
                lattice.put(idx, idx + 1, jaso_unit, SYMBOL.SW, self.model.pos_table.get_id(SYMBOL.SW), -10000.0)
        elif StringUtil.is_korean(hex_value) is False and StringUtil.is_japanese(
                hex_value) is False and StringUtil.is_chinese(hex_value):
            lattice.put(idx, idx + 1, jaso_unit, SYMBOL.SW, self.model.pos_table.get_id(SYMBOL.SW), -10000.0)

    def chunk_letter_parsing(self, lattice, jaso_unit, idx, chunk_letter):
        cur_pos = ""
        hex_value = ord(jaso_unit)
        if StringUtil.is_english(hex_value):
            cur_pos = "SL"
        elif StringUtil.is_num(hex_value):
            cur_pos = "SN"
        elif StringUtil.is_chinese(hex_value):
            cur_pos = "SH"
        elif StringUtil.is_japanese(hex_value):
            cur_pos = "SL"

        if cur_pos == chunk_letter.get_prev_pos():
            chunk_letter.set_prev_word(chunk_letter.get_prev_word() + jaso_unit)
        else:
            if chunk_letter.get_prev_pos() == "SL" or chunk_letter.get_prev_pos() == "SH" or chunk_letter.get_prev_pos() == "SN":
                lattice.put(begin_idx=chunk_letter.get_prev_begin_idx(),
                            end_idx=idx,
                            word=chunk_letter.get_prev_word(),
                            pos=chunk_letter.get_prev_pos(),
                            pos_id=self.model.pos_table.get_id(chunk_letter.get_prev_pos()),
                            observation_score=-1.0)
            chunk_letter.set_prev_begin_idx(idx)
            chunk_letter.set_prev_word(jaso_unit)
            chunk_letter.set_prev_pos(cur_pos)

    def consume_remain_chunk_letter(self, lattice, idx, chunk_letter):
        if len(chunk_letter.get_prev_pos().strip()) != 0:
            lattice.put(begin_idx=chunk_letter.get_prev_begin_idx(),
                        end_idx=idx,
                        word=chunk_letter.get_prev_word(),
                        pos=chunk_letter.get_prev_pos(),
                        pos_id=self.model.pos_table.get_id(chunk_letter.get_prev_pos()),
                        observation_score=-1.0)

# komoran = Komoran("../training/komoran_model")
# komoran.set_fwd("../fwd.dic")
# komoran.set_user_dic("../user.dic")
# print(komoran.analyze("이번 감기는 강하다"))
# print()
# print(komoran.analyze("골렸어"))
# print()
# print(komoran.analyze("샀으니"))
# print()
# print(komoran.analyze("이어져서"))  # --> 이어지/VV 어서/EC 가 정답임
# print()
# print(komoran.analyze("러너라는"))  # --> 러너/NNG 이라는
# print()
# print(komoran.analyze("이정도로 골렸어 뷁"))
# print()
# print(komoran.analyze("뷁뷁 뷁부어"))
# print()
#
# ch = '감'
# hex_value = ord(ch)
# if 0x0000 < hex_value < 0x007E:
#     print('basic latic')
# else:
#     print('other')
