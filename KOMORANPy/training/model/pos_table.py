class PosTable:
    def __init__(self):
        self.pos_id_table = {}
        self.id_pos_table = {}

    def put(self, pos):
        if pos not in self.pos_id_table:
            self.pos_id_table[pos] = len(self.pos_id_table)
            self.id_pos_table[len(self.id_pos_table)] = pos

    def get_id(self, pos):
        return self.pos_id_table.get(pos)

    def get_pos(self, pos_id):
        return self.id_pos_table.get(pos_id)

    def size(self):
        return len(self.pos_id_table)

    def save(self, filename):
        with open(filename, 'w') as f:
            for pos, pos_id in self.pos_id_table.items():
                f.write(f"{pos}\t{pos_id}\n")
        # todo : 세종 테그셋 id를 빌드하는 부분은 생략 됨

    def load(self, filename):
        with open(filename, 'r') as f:
            self.__init__()
            for line in f.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                pos, pos_id = line.split('\t')
                self.pos_id_table[pos] = int(pos_id)
                self.id_pos_table[int(pos_id)] = pos
        # todo : 세종 테그셋 id를 빌드하는 부분은 생략 됨


# pos_table = PosTable()
# pos_table.put('NNG')
# pos_table.put('NNP')
# pos_table.put('NNG')
# pos_table.put('NNK')
# pos_table.save("wow.table")
# pos_table.load("wow.table")
