class IrregularNode:

    def get_first_pos_id(self):
        return self.first_pos_id

    def set_first_pos_id(self, pos_id):
        self.first_pos_id = pos_id

    def set_tokens(self, irr_node_tokens):
        self.irr_node_tokens = irr_node_tokens

    def get_tokens(self):
        return self.irr_node_tokens
