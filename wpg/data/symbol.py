class Symbol:

    global_id = 1

    def __init__(self, value):
        self.value = value
        self.id = Symbol.global_id
        Symbol.global_id += 1

    def get_rep(self):
        return repr(self.value)

class SymbolString:
    def __init__(self, literal, array):
        self.literal = literal
        self.array = array
        pass
