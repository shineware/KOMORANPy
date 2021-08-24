class IrregularNode:

    def get_first_pos_id(self):
        return self.first_pos_id

    def set_first_pos_id(self, pos_id):
        self.first_pos_id = pos_id

    def set_tokens(self, irr_node_tokens):
        self.irr_node_tokens = irr_node_tokens

    def get_tokens(self):
        return self.irr_node_tokens

    def __eq__(self, other):
        if isinstance(other, IrregularNode):
            return self.first_pos_id == other.first_pos_id and self.irr_node_tokens == other.irr_node_tokens
        return False

    def __repr__(self):
        return f"(first_pos_id={self.first_pos_id}, irr_node_tokens={self.irr_node_tokens})"
