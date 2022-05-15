from node import *
from lexical_analyze_with_nonGui import lexical
import prettytable as pt

class syntax(object):
    def __init__(self):
        super(syntax, self).__init__()
        self.productions=[]     #产生式
        self.terminate=set()       #终结符
        self.nonterminate=set()    #非终结符
        self.elements=set()      #所有终结符和非终结符
        self.firstSet={}         #first集
        self.productions_dict={}    #一个映射，给出一个非终结符，列出所有的等式左边含有其的式子
        self.status={}           #字典，根据状态号映射出项集
        self.objectSets={}       #字典,映射出闭包的状态号
        self.errorLine={}        #字典，根据token表中的行数映射出所在代码的行数
        self.action_goto_table={} #action/goto表
        self.DFA=DFA(set())

        self.procedure=[]       #用于与pyqt联动


    def read_grammar(self, syntax_grammar_path):
        for line in open(syntax_grammar_path, 'r', encoding='UTF-8'):
            if line[0]=='\n':        #去掉注释
                continue
            if line[0]=='#':        #去掉注释
                continue
            line = line[:-1]    #去掉换行符
            left = line.split('->')[0]
            right = line.split('->')[1]
            #print(left,right)
            right_list = []
            if right.find(' ') != -1:
                right_list = right.split(' ')
            else:
                right_list.append(right)
            production = {}
            production[left] = right_list
            self.productions.append(production)

    def get_terminate_nonterminate(self):
        for production in self.productions:
            for left in production.keys():
                if left not in self.productions_dict:
                    self.productions_dict[left] = []
                self.productions_dict[left].append((
                    tuple(production[left]),
                    self.productions.index(production)))
                self.elements.add(left)         #原理：因为所以非终结符都会出现在产生式左边，也只有非终结符会出现在产生式的左边
                self.nonterminate.add(left)
                for right in production[left]:
                    self.elements.add(right)
        self.terminate = self.elements - self.nonterminate


    def init_first_set(self):
        for terminate in self.terminate:
            self.firstSet[terminate] = {terminate}
        for nonterminate in self.nonterminate:
            self.firstSet[nonterminate] = self.get_first_set(
                nonterminate, set())

    def get_first_set(self, cur_status, all_elem):    #这里我们可以采用递归求解
        if cur_status in self.firstSet.keys():
            return self.firstSet[cur_status]
        all_elem.add(cur_status)
        cur_status_set = set()
        for right_list in self.productions_dict[cur_status]:
            for right in right_list[0]:
                right_set = None
                if right in all_elem:   #防止出现类似于左递归的现象
                    continue
                if right in self.firstSet.keys():
                    right_set = self.firstSet[right]
                else:
                    right_set = self.get_first_set(right, all_elem)
                cur_status_set=cur_status_set.union(right_set)
                if '$' not in right_set:
                    break
        self.firstSet[cur_status]=cur_status_set
        return cur_status_set

    #无问题
    def closure(self, cur_production, ex_object_set):
        #print(self.terminate)
        ex_object_set.add(cur_production)  # (0, 'start1', ('start',), 0, '#'), set())
        right = cur_production[2]
        point_index = cur_production[3]
        tail_set = cur_production[4]
        #print('self.nonterminate',self.nonterminate)
        if point_index < len(right) and \
                (right[point_index] in self.nonterminate):
            #print('self.productions_dict[right[point_index]]',right[point_index],self.productions_dict[right[point_index]])
            for pro_right in self.productions_dict[right[point_index]]:
                #print('pro_right',pro_right)
                new_tail_set = set()
                flag = True
                for i in range(point_index + 1, len(right)):
                    cur_first_set = self.firstSet[right[i]]
                    if '$' in cur_first_set:
                        new_tail_set = tuple(
                            set(new_tail_set) | (cur_first_set - set('$')))
                    else:
                        flag = False
                        new_tail_set = tuple(
                            set(new_tail_set) | cur_first_set)
                        break
                if flag:
                    new_tail_set = tuple(set(new_tail_set) | set(tail_set))
                ex_new_production = (
                    pro_right[1],
                    right[point_index], pro_right[0], 0, new_tail_set)
                #print('ex_object_set',ex_object_set)
                if ex_new_production not in ex_object_set:
                    #print('ex_new_production',ex_new_production)
                    ex_object_set |= self.closure(
                        ex_new_production, ex_object_set)
            new_ex_object_set = {}
            for eos in ex_object_set:
                pro_key = (eos[0], eos[1], eos[2], eos[3])
                if tuple(pro_key) not in new_ex_object_set:
                    new_ex_object_set[tuple(pro_key)] = set()
                new_ex_object_set[pro_key] |= set(eos[4])
            ex_object_set = set()
            for key in new_ex_object_set:
                production = (key[0], key[1], key[2], key[
                    3], tuple(new_ex_object_set[key]))
                ex_object_set.add(tuple(production))
        #print(ex_object_set)
        return ex_object_set

    def find_LR1_node(self,set_id):
        if set_id in self.status:
            return self.status[set_id]
        return LR1Node(set_id=set_id)

    def init_action_goto_table(self):
        set_id = 0
        new_node = self.find_LR1_node(set_id)
        object_set = self.closure(
             (0, 'start1', ('start',), 0, '#'), set())
        #print('object_set', object_set)
        new_node.add_object_set_by_set(object_set)
        self.objectSets[tuple(object_set)] = set_id  # 字典
        self.status[set_id] = new_node  # 字典
        object_set_queue = list()
        object_set_queue.append(new_node)
        while object_set_queue:
            top_object_node = object_set_queue.pop(0)
            old_set = top_object_node.object_set
            old_set_id = top_object_node.set_id
            for cur_production in old_set:
                production_id = cur_production[0]
                left = cur_production[1]
                right = cur_production[2]
                point_index = cur_production[3]
                tail_set = cur_production[4]
                if point_index == len(right) or '$' in right:
                    if old_set_id not in self.action_goto_table:
                        self.action_goto_table[old_set_id] = {}
                    for tail in tail_set:
                        if tail in self.action_goto_table[old_set_id]:   #存在规约-规约冲突
                            assert False ,'the grammar is not a LR(1) grammar!!!'
                            return
                        self.action_goto_table[old_set_id][tail] = ('r', production_id)
                elif point_index>len(right):    #新增
                    continue
                else:
                    tar_set_id = 0
                    new_production = (production_id, left, right,
                                      point_index + 1, tail_set)
                    new_object_set = self.closure(
                         new_production, set())
                    if tuple(new_object_set) in self.objectSets.keys():
                        tar_set_id = self.objectSets[tuple(new_object_set)]
                    else:
                        set_id += 1
                        tar_set_id = set_id
                        self.objectSets[tuple(new_object_set)] = set_id
                        new_node = self.find_LR1_node(tar_set_id)
                        new_node.add_object_set_by_set(new_object_set)
                        self.status[tar_set_id] = new_node
                        object_set_queue.append(new_node)
                    if old_set_id not in self.action_goto_table:
                        self.action_goto_table[old_set_id] = {}
                    if right[point_index] in self.terminate:
                        self.action_goto_table[old_set_id][
                            right[point_index]] = ('s', tar_set_id)
                    else:
                        self.action_goto_table[old_set_id][
                            right[point_index]] = ('g', tar_set_id)
        self.DFA.status = self.status

    def run_on_lr_dfa(self, tokens):
        tb=pt.PrettyTable(['符号栈', '状态栈','剩余输入串','动作'])
        status_stack = [0]
        symbol_stack = ['#']
        success = False
        tokens.reverse()
        #print(tokens)
        row = 1
        while not success:
            action_str=''
            #tb.add_row([symbol_stack.__str__(), status_stack.__str__()]) #这是一个非常奇怪的bug，不加__str__()就无法成功
            current_state = status_stack[-1]
            print( 'token =', tokens[-1])
            #print(tokens)
            #print(symbol_stack,status_stack)
            #print('123',self.action_goto_table[current_state])
            if tokens[-1] in self.action_goto_table[current_state]:
                action = self.action_goto_table[current_state][tokens[-1]]
                if action[0] == 's':    #移进
                    action_str=f'移入{action[1]}'
                    row=row+1
                    status_stack.append(action[1])
                    symbol_stack.append(tokens[-1])
                    tokens = tokens[:-1]
                elif action[0] == 'r':  #归约
                    production = self.productions[action[1]]
                    left = list(production.keys())[0]
                    right_len = len(production[left])
                    tem_str=production.keys().__str__()[12:-3] + ' -> ' + production[left].__str__()[1:-1]
                    action_str = '规约'+tem_str
                    if action[1] == 0:
                        tb.add_row(['[]','[]','[]','分析完成!'])
                        print(tb)
                        print( 'Syntax anaysis successfully!')
                        output=open('syntax_result.txt','w+')
                        output.write('%s'%tb);
                        success = True
                        break

                    #print(production[left].__str__())
                    tokens.append(left)
                    row=row-1
                    if production[left] == ['$']:
                        continue
                    status_stack = status_stack[:-right_len]
                    symbol_stack = symbol_stack[:-right_len]
                elif action[0] == 'g':  #转移状态
                    action_str = f'GOTO {action[1]}'
                    row = row + 1
                    status_stack.append(action[1])
                    symbol_stack.append(tokens[-1])
                    tokens = tokens[:-1]
            else:
                row = row - 1
                print('[期望输入,动作，跳转状态]: ',self.action_goto_table[current_state])
                print("当前项集:", self.status[current_state].object_set)
                #print("hi", self.status[old_set_id])
                #print(tb)
                print(f'Syntax error in token_table at row {row}! Also corresponding to your code at row {self.errorLine[row]}\n')
                print(f'The error exists before {tokens[-1]}')

                output = open('syntax_false_result.txt', 'w+')
                output.write('%s' % tb);
                break
            tb.add_row([symbol_stack.__str__(), status_stack.__str__(),tokens.__str__(),action_str])  # 这是一个非常奇怪的bug，不加__str__()就无法成功
            self.procedure.append([status_stack.__str__(),symbol_stack.__str__(),tokens.__str__(),action_str.__str__()])


    def read_and_analyze(self, filename):
        token_table = open(filename, 'r')
        tokens = []
        row=1
        for line in token_table:
            self.errorLine[row] = line.split(' ')[2]
            row+=1
            line = line[:-1]
            tokens.append(line.split(' ')[0])
        tokens.append('#')
        self.run_on_lr_dfa(tokens)

    def main_process(self):
        lexical_analyzer = lexical()
        lexical_analyzer.read_grammar('lexical_grammar')
        lexical_analyzer.build_nfa()
        lexical_analyzer.nfa_to_dfa()
        lexical_analyzer.start_lexical_analyze('inputcode.c')

        syntax_analyzer = syntax()
        syntax_analyzer.read_grammar('syntax_grammar')
        syntax_analyzer.get_terminate_nonterminate()
        syntax_analyzer.init_first_set()
        syntax_analyzer.init_action_goto_table()
        syntax_analyzer.read_and_analyze('token_table.data')

def main():
    lexical_analyzer = lexical()
    lexical_analyzer.read_grammar('lexical_grammar')
    lexical_analyzer.build_nfa()
    lexical_analyzer.nfa_to_dfa()
    lexical_analyzer.start_lexical_analyze('inputcode.c')

    syntax_analyzer = syntax()
    # syn_ana.read_syntax_grammar('sample_syn_grammar.txt')
    syntax_analyzer.read_grammar('syntax_grammar')
    syntax_analyzer.get_terminate_nonterminate()
    syntax_analyzer.init_first_set()
    syntax_analyzer.init_action_goto_table()
    print(syntax_analyzer.action_goto_table)
    syntax_analyzer.read_and_analyze('token_table.data')


if __name__ == '__main__':
    main()
