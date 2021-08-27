class FindContext:
    def __init__(self, init_node):
        self.current_node = init_node

    def set_current_node(self, node):
        self.current_node = node

    def get_current_node(self):
        return self.current_node

    def get_current_fail_node(self):
        return self.current_node.get_fail_node()

    def get_current_child_nodes(self):
        return self.current_node.get_child_nodes()

    def is_root(self):
        return self.current_node.get_parent_node() is None
