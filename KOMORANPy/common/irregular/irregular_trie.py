from ..ahocorasick.ahocorasick_dictionary import AhoCorasickDictionary


class IrregularTrie:
    def __init__(self):
        self.ahocorasick = AhoCorasickDictionary()

    def put(self, irr_pattern, irr_node):
        irr_nodes = self.ahocorasick.get_value(irr_pattern)
        if irr_nodes is None:
            irr_nodes = [irr_node]
        else:
            include_same_node = False
            for _irr_node in irr_nodes:
                if irr_node == _irr_node:
                    include_same_node = True
                    break
            if not include_same_node:
                irr_nodes.append(irr_node)
        self.ahocorasick.put(irr_pattern, irr_nodes)

    def get_dictionary(self):
        return self.ahocorasick

    def save(self, filename):
        self.ahocorasick.save(filename)

    def load(self, filename):
        self.ahocorasick.load(filename)
