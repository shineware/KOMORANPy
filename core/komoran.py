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
        self.begin_idx = begin_idx
        self.end_idx = end_idx
        self.word = word
        self.pos = pos
        self.pos_id = pos_id
        self.score = score


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

    @staticmethod
    def regular_parsing(lattice, jaso_unit, idx):
        print(lattice.get_observation(jaso_unit))

