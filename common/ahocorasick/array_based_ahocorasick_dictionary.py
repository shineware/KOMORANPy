import gzip
import pickle

from common.ahocorasick.array_based_ahocorasick_node import AhoCorasickNode
from common.ahocorasick.find_context import FindContext


class AhoCorasickDictionary:
    def __init__(self):
        self.root_node = AhoCorasickNode()
        self.root_node.set_depth(0)

    def put(self, keys, value):
        current_node = self.root_node
        for depth, key in enumerate(keys):
            child_nodes = current_node.get_child_nodes()
            if len(child_nodes) == 0:
                node = AhoCorasickNode()
                node.set_parent_node(current_node)
                node.set_depth(depth + 1)
                node.set_key(key)
                child_nodes.append(node)
                current_node.set_child_nodes(child_nodes)
                current_node = current_node.get_child_nodes()[0]
            else:
                child_node = self.find_child_node(child_nodes, key)
                if child_node is None:
                    node = AhoCorasickNode()
                    node.set_parent_node(current_node)
                    node.set_depth(depth + 1)
                    node.set_key(key)
                    self.insert_child_node(child_nodes, node)
                    current_node.set_child_nodes(child_nodes)
                    child_node = node
                current_node = child_node

        current_node.set_value(value)

    def get(self, key, context):
        result_dic = {}
        while True:
            # return array
            child_nodes = context.get_current_child_nodes()
            if len(child_nodes) == 0:
                fail_node = context.get_current_fail_node()
                if fail_node is None:
                    return None
                else:
                    context.set_current_node(fail_node)
                continue
            child_node = self.find_child_node(child_nodes, key)
            if child_node is None:
                if context.get_current_node() != self.root_node:
                    context.set_current_node(context.get_current_fail_node())
                    continue
            else:
                if child_node.get_value() is not None:
                    result_dic[self.get_key_from_root(child_node)] = child_node.get_value()
                while child_node.get_fail_node() is not None:
                    if child_node.get_fail_node().get_value() is not None:
                        result_dic[
                            self.get_key_from_root(child_node.get_fail_node())] = child_node.get_fail_node().get_value()
                    child_node = child_node.get_fail_node()
                context.set_current_node(self.find_child_node(child_nodes, key))
            break
        return result_dic

    def get_value(self, keys):
        node = self.root_node
        for key in keys:
            child_nodes = node.get_child_nodes()
            if len(child_nodes) == 0:
                return None
            node = self.find_child_node(child_nodes, key)
            if node is None:
                return None
        return node.get_value()

    def build_fail_link(self):
        current_node = self.root_node
        queue = [current_node]

        while len(queue) != 0:
            current_node = queue.pop(0)
            self._link_fail_node(current_node)
            for node in current_node.get_child_nodes():
                queue.append(node)

    def _link_fail_node(self, current_node):
        if current_node == self.root_node:
            pass
        elif current_node.get_parent_node() == self.root_node:
            current_node.set_fail_node(self.root_node)
        else:
            fail_node = current_node.get_parent_node().get_fail_node()
            while fail_node != self.root_node:
                if len(fail_node.get_child_nodes()) == 0:
                    fail_node = fail_node.get_fail_node()
                    continue
                child_node = self.find_child_node(fail_node.get_child_nodes(), current_node.get_key())
                if child_node is not None:
                    current_node.set_fail_node(child_node)
                    break
                fail_node = fail_node.get_fail_node()
            if current_node.get_fail_node() is None:
                child_node = self.find_child_node(self.root_node.get_child_nodes(), current_node.get_key())
                if child_node is not None:
                    current_node.set_fail_node(child_node)
                else:
                    current_node.set_fail_node(self.root_node)

    def new_find_context(self):
        return FindContext(self.root_node)

    def get_key_from_root(self, child_node):
        current_node = child_node
        key = ""
        while current_node != self.root_node:
            key = current_node.get_key() + key
            current_node = current_node.get_parent_node()
        return key

    def save(self, filename):
        with gzip.open(filename, 'wb') as f:
            pickle.dump(self.root_node, f)

    def load(self, filename):
        with gzip.open(filename, 'rb') as f:
            self.root_node = pickle.load(f)

    def find_child_node(self, child_nodes, key):
        head = 0
        tail = len(child_nodes) - 1
        idx = -1
        is_found = False
        while head <= tail:
            idx = int((head+tail)/2)
            if child_nodes[idx].get_key() < key:
                head = idx + 1
            elif child_nodes[idx].get_key() > key:
                tail = idx - 1
            elif child_nodes[idx].get_key() == key:
                is_found = True
                break
        if is_found:
            return child_nodes[idx]
        else:
            return None

    def insert_child_node(self, child_nodes, node):
        head = 0
        tail = len(child_nodes)
        while head < tail:
            idx = (head + tail) // 2
            if node.get_key() < child_nodes[idx].get_key():
                tail = idx
            else:
                head = idx + 1
        child_nodes.insert(head, node)

# import bisect
# mylist = ['aa', 'b', 'f']
# idx = bisect.bisect(mylist, 'aa')
# print(idx)
# print(mylist[idx-1])
# print(mylist)

# dic = AhoCorasickDictionary()
# dic.put("감기", "NNG")
# dic.put("감", "NNP")
# dic.put("기", "NNP")
# dic.build_fail_link()
# context = dic.new_find_context()
# for a in ["감", "기"]:
#     print(a)
#     print(dic.get(a, context))