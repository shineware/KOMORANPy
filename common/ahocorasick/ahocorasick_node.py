class AhoCorasickNode:
    def __init__(self):
        self.child_nodes = {}
        self.parent_node = None
        self.fail_node = None
        self.key = None
        self.value = None
        self.depth = -1

    def get_child_nodes(self):
        return self.child_nodes

    def set_child_nodes(self, children):
        self.child_nodes = children

    def get_parent_node(self):
        return self.parent_node

    def set_parent_node(self, node):
        self.parent_node = node

    def get_fail_node(self):
        return self.fail_node

    def set_fail_node(self, node):
        self.fail_node = node

    def get_depth(self):
        return self.depth

    def set_depth(self, depth):
        self.depth = depth

    def get_key(self):
        return self.key

    def set_key(self, key):
        self.key = key

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def __str__(self):
        return f"child_nodes={self.child_nodes}, parent_node={self.parent_node}, fail_node={self.fail_node}, " \
               f"key={self.key}, value={self.value}, depth={self.depth} "
