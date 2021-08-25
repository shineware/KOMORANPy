import datetime
import math

from common.irregular.irregular_trie import IrregularTrie
from constant import FILENAME, SYMBOL
from parser.korean_unit_parser import KoreanUnitParser
from training.model.observation import Observation
from training.model.pos_table import PosTable
from training.model.transition import Transition


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
            # todo : for 문을 돌면서 list에서 pos에 해당하는 score 값을 찾아야 하기 때문에 이 부분은 추후 개선의 여지가 필요함
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
                print(f"pos_id is -1! : {prev_lattice_node}")
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


class Komoran:
    def __init__(self, model_path):
        print(f'load model : {model_path}')
        self.model = Model(model_path)
        self.unit_parser = KoreanUnitParser()
        self.user_dic = None
        print(f'load done')

    def set_user_dic(self, user_dic_path):
        self.user_dic = Observation()
        with open(user_dic_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#':
                    continue
                tokens = line.rsplit('/', 1)
                if len(tokens) == 1:
                    word = tokens[0]
                    pos = "NNP"
                else:
                    word = tokens[0]
                    pos = tokens[1]
                self.user_dic.put(word, pos, self.model.pos_table.get_id(pos), 0.0)
        self.user_dic.get_dictionary().build_fail_link()

    def analyze(self, sentence):
        lattice = Lattice(self.model, self.user_dic)
        jaso_units = self.unit_parser.parse(sentence)
        irr_idx = -1
        for idx, jaso_unit in enumerate(jaso_units):
            # todo : here we go! 띄어쓰기 로직 추가
            self.regular_parsing(lattice, jaso_unit, idx)
            irr_idx = self.irregular_parsing(lattice, jaso_unit, idx, irr_idx)
            self.irregular_extends(lattice, jaso_unit, idx)

        last_idx = len(jaso_units)
        # 단어 끝에 어절 마지막 노드 추가
        lattice.put(last_idx, last_idx + 1, SYMBOL.EOE, SYMBOL.EOE, self.model.pos_table.get_id(SYMBOL.EOE), 0)
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
        for word, pos in reversed(result):
            print(f"{word}/{pos}")

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

    def irregular_parsing(self, lattice, jaso_unit, idx, irr_idx):
        # get_irregular_nodes 는 아래와 같은 형태가 리턴 됨
        # {
        #   'ㄱㅏ': [('ㅇㅓ', 15), ('ㄱㅏ', 27), ('ㅇㅏ', 15)]
        # }
        word_with_irr_nodes = lattice.get_irregular_nodes(jaso_unit)
        if len(word_with_irr_nodes) == 0:
            return irr_idx
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
                    irr_idx -= 1
                else:
                    cnt = 0
                    for _word, pos, pos_id, observation_score in word_with_pos_scores:
                        if cnt == 0:
                            lattice.put(begin_idx, irr_idx, _word, pos, pos_id, observation_score, True)
                        elif cnt == len(word_with_pos_scores) - 1:
                            lattice.put(irr_idx + 1, end_idx, _word, pos, pos_id, observation_score, True)
                        else:
                            lattice.put(irr_idx + 1, irr_idx, _word, pos, pos_id, observation_score, True)
                        irr_idx -= 1
                        cnt += 1
        return irr_idx

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


komoran = Komoran("../training/komoran_model")
begin_time = datetime.datetime.now()
komoran.analyze("골렸어")  # --> 골리/VV 었/EP 어/EC 가 정답임
komoran.analyze("샀으니")  # --> 사/VV 았/EP 으니/EC 가 정답임
komoran.analyze("이어져서")  # --> 이어지/VV 어서/EC 가 정답임
komoran.analyze("러너라는")  # --> 러너/NNG 이라는
komoran.analyze("을ㅋ박라퀩겼")
end_time = datetime.datetime.now()
delta = end_time - begin_time
print(delta.total_seconds() * 1000)
# lattice = Lattice(komoran.model, komoran.user_dic)
# lattice.split_irr_nodes([('ㄱㅗㄹㄹㅣ', 14), ('ㅇㅓ', 15)])
