

from node import *
class lexical(object):
    def __init__(self):
        super(lexical, self).__init__()
        self.productions=[]       #规则集合
        self.utils={}       #自然数digit，正数positive，字母表alphabet
        self.keywords={}    #关键字
        self.NFANodes={}       #所有的nfa节点 数据结构为map<string,NFANode> 键值string是节点名称
        self.DFANodes = {}  # 所有的dfa节点 数据结构为map<string,NFANode> 键值string是节点名称
    def read_grammar(self,lexical_grammar_path):
        row=0
        for line in open(lexical_grammar_path,'r'):
            row+=1
            div_arrow=line.find('->')
            left=line[0:div_arrow]
            right= line[div_arrow+2:len(line)-1]  #去掉结尾的换行符
            if row<4:   #记录自然数，正数，和字母
                right = right.split('|')
                self.utils[left] = right
                continue
            elif row == 4:  #记录关键字
                right = right.split('|')
                for keyword in right:
                    self.keywords[keyword]=left
                continue
            else:           #记录规则
                div_blank=right.find(' ')
                production={}
                production['left'] = left
                if div_blank != -1:
                    production['input'] = right[0:div_blank]
                    production['right'] = right[div_blank + 1:len(right)]
                else:
                    production['input'] = right
                    production['right'] = None
                self.productions.append(production)

    def find_nfa_node(self,name,node_type):
        if name in self.NFANodes:
            node = self.NFANodes[name]
        else:
            node = NFANode(name=name, type=node_type)
        return node

    def build_nfa(self):
        start_node = self.find_nfa_node('start', 0)
        end_node = self.find_nfa_node('end', 1)
        self.NFANodes['start'] = start_node
        self.NFANodes['end'] = end_node
        for production in self.productions:
            name = production['left']
            alpha = production['input']
            right = production['right']
            node = self.find_nfa_node(name, 0)
            target_node={}
            if right is not None:
                target_node = self.find_nfa_node(right, 0)
            if alpha not in self.utils.keys():  # alpha是输入的一些限制符，或运算符
                if right is None:
                    node.add_edge(alpha, 'end')
                else:
                    if right in self.utils:
                        for val in self.utils[right]:
                            node.add_edge(alpha, val)
                    else:
                        node.add_edge(alpha, right)
            else:  # alpha是数字，字母或者关键字
                for val in self.utils[alpha]:
                    if right is None:
                        node.add_edge(val, 'end')
                    else:
                        if right in self.utils:
                            for val in self.utils[right]:
                                node.add_edge(alpha, val)
                        else:
                            node.add_edge(alpha, right)
                            node.add_edge(val, right)
            self.NFANodes[name] = node
            if right is not None:
                self.NFANodes[right] = target_node

        alphabets = set()
        for i in range(ord(' '), ord('~') + 1):  # 这样就能包含所有能够看见的符号了
            alphabets.add(chr(i))
        self.NFA = NFA(alphabets)
        self.NFA.status = self.NFANodes

    def find_dfa_node(self,name,node_type):
        if name in self.DFANodes:
            node = self.DFANodes[name]
        else:
            node = DFANode(name=name, type=node_type)
        return node

    def nfa_to_dfa(self):
        for node_name in self.NFA.status['start'].edge['$']:
            start_node = self.find_dfa_node('start', 0)
            dfa_node = self.find_dfa_node(node_name, 0)
            start_node.add_edge('$', node_name)
            self.DFANodes['start'] = start_node
            self.DFANodes[node_name] = dfa_node
            is_visit = set()
            queue = list()
            nfa_node_set = set()
            nfa_node_set.add(node_name)
            queue.append((nfa_node_set, node_name))
            while queue:
                node_name = queue.pop(0)
                top_node_name = node_name[0]
                dfa_node_name = node_name[1]
                dfa_node = self.find_dfa_node(dfa_node_name, 0)
                for alpha in self.NFA.alphabets:
                    target_set = set()
                    for nfa_node_name in top_node_name:
                        nfa_name = self.NFA.status[nfa_node_name]
                        if alpha in nfa_name.edge.keys():
                            for name in nfa_name.edge[alpha]:
                                target_set.add(name)
                    if not target_set:
                        continue
                    dfa_new_node_name = ''
                    _type = 0
                    tmp_list = list(target_set)
                    target_list = sorted(tmp_list)
                    for tar in target_list:
                        dfa_new_node_name = '%s$%s' % (dfa_new_node_name, tar)
                        _type += int(self.NFA.status[tar].type)
                    if _type > 0:
                        _type = 1
                    dfa_new_node = self.find_dfa_node(dfa_new_node_name, _type)
                    dfa_node.add_edge(alpha, dfa_new_node_name)
                    self.DFANodes[dfa_node_name] = dfa_node
                    self.DFANodes[dfa_new_node_name] = dfa_new_node
                    if dfa_new_node_name in is_visit:
                        continue
                    else:
                        is_visit.add(dfa_new_node_name)
                        queue.append((target_set, dfa_new_node_name))
        alphabets = set()
        for i in range(ord(' '), ord('~') + 1):
            alphabets.add(chr(i))
        self.DFA = DFA(alphabets)
        self.DFA.status = self.DFANodes

    def analyze_by_line(self, line, pos):
        for dfa_name in self.DFA.status['start'].edge['$']:
            cur_pos = pos
            token_value = ''
            token_name = dfa_name
            current_node = self.DFA.status[dfa_name]
            while cur_pos < len(line) and line[cur_pos] in current_node.edge.keys():
                token_value += line[cur_pos]
                current_node = self.DFA.status[list(current_node.edge[line[cur_pos]])[0]]
                cur_pos += 1
            if current_node.type > 0:
                if token_value in self.keywords.keys():
                    token_name = 'keyword'
                return cur_pos - 1, token_name, token_value
        return pos, None, ''

    def start_lexical_analyze(self, file_name):
        line_num = 0
        lex_error = False
        token_table = []
        for line in open(file_name, 'r',encoding='utf-8'):
            pos = 0
            line_num += 1
            if line[0]=='/' and line[1]=='/':
                continue
            line = line.split('\n')[0]
            while pos < len(line) and not lex_error:
                while pos < len(line) and line[pos] in ['\t', '\n', ' ', '\r']: #过滤掉多余字符
                    pos += 1
                if pos < len(line):
                    pos, token_name, token_value = self.analyze_by_line(line, pos)
                    if token_name is None:
                        print ('Lexical error at line %s, column %s' % (
                            (str(line_num), str(pos))))
                        lex_error = True
                        break
                    else:
                        token_table.append((token_name, token_value,line_num,pos))
                        print ('(%s\t, %s\t,%s\t, %s)' % (line_num,pos, token_name, token_value))
                    pos += 1
        if not lex_error:
            output = open('token_table.data', 'w+', encoding='UTF-8')
            for token_name, token_value ,line_num,pos in token_table:
                type_of_token = token_value
                if token_name == 'identifier' or token_name == 'number':
                    type_of_token = token_name
                output.write('%s %s %s %s\n' % (type_of_token, token_value,line_num,pos))
            output.close()
            return True
        return False

def main():
    lexical_analyzer = lexical()
    lexical_analyzer.read_grammar('lexical_grammar')
    lexical_analyzer.build_nfa()
    lexical_analyzer.nfa_to_dfa()
    lexical_analyzer.start_lexical_analyze('inputCode.c')

if __name__ == '__main__':
    main()





