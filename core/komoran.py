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

    def __repr__(self):
        return f"""(begin_idx={self.__begin_idx}, end_idx={self.end_idx}, word={self.word}, pos={self.pos}, pos_id={self.pos_id}, score={self.score}, prev_nod_idx={self.prev_node_idx})"""

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


class Lattice:
    def __init__(self, model, user_dic):
        self.model = model
        self.user_dic = user_dic
        self.init_node()
        self.make_new_contexts()

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

    def put(self, begin_idx, end_idx, word, pos, pos_id, observation_score):
        prev_lattice_nodes = self.lattice.get(begin_idx)
        if prev_lattice_nodes is None:
            return False
        else:
            max_lattice_node = self.get_max_transition_node(prev_lattice_nodes, begin_idx, end_idx, word, pos, pos_id,
                                                            observation_score)
            if max_lattice_node is not None:
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
            # 불규칙인 경우
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


class Komoran:
    def __init__(self, model_path):
        self.model = Model(model_path)
        self.unit_parser = KoreanUnitParser()
        self.user_dic = None

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
        for idx, jaso_unit in enumerate(jaso_units):
            # todo : here we go! 각종 파서 개발 필요
            self.regular_parsing(lattice, jaso_unit, idx)

        last_idx = len(jaso_units)
        # 단어 끝에 어절 마지막 노드 추가
        lattice.put(last_idx, last_idx + 1, SYMBOL.EOE, SYMBOL.EOE, self.model.pos_table.get_id(SYMBOL.EOE), 0)
        last_idx += 1

        for i in range(0, last_idx + 1):
            lattice_nodes = lattice.lattice.get(i)
            if lattice_nodes is None:
                continue
            print(f'{i} :')
            for lattice_node in lattice_nodes:
                print(f'\t{lattice_node}')

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


komoran = Komoran("../training/komoran_model")
komoran.analyze("감기는")
