class NFANode(object):
    def __init__(self, name=None, type=0):
        super(NFANode, self).__init__()
        self.name = name
        self.type = type
        self.edge = {}

    def add_edge(self, alpha, target):
        if alpha not in self.edge:
            targets = set()
            targets.add(target)
            self.edge[alpha] = targets  #对应于一个输出多个边
        else:
            self.edge[alpha].add(target)


class NFA(object):
    def __init__(self, alphabets):
        super(NFA, self).__init__()
        self.status = {}
        self.alphabets = alphabets

    def get_target(self, cur_status, alpha):
        if cur_status in self.status:
            if alpha in self.status[cur_status]:
                return self.status[cur_status][alpha]
        return None

class DFANode(object):
    def __init__(self, name, type=None):
        super(DFANode, self).__init__()
        self.name = name
        self.type = type
        self.edge = {}

    def add_edge(self, alpha, target):
        if alpha not in self.edge:
            targets = set()
            targets.add(target)
            self.edge[alpha] = targets
        else:
            self.edge[alpha].add(target)

class DFA(object):
    def __init__(self, alphabets):
        super(DFA, self).__init__()
        self.status = {}
        self.alphabets = alphabets

class LR1Node(object):
    def __init__(self, set_id):
        self.set_id = set_id    #项集号
        self.object_set = set() #项集

    def add_object_set(self, id, left, right, index, tail):
        tmp = (id, left, right, index, tail)
        if tmp not in self.object_set:
            self.object_set.add(tmp)

    def add_object_set_by_set(self, object_set):
        self.object_set |= object_set