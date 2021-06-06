from sly import Lexer
from sly import Parser
from copy import copy
import sys

class BasicLexer(Lexer):
    tokens = { NAME, NUMBER, STRING, IF, THEN, ELSE, FOR, FUNC, TO, ARROW, AND, OR, EQEQ, NE, GT, GE, LT, LE, INCREMENT, DECREMENT}
    ignore = '\t '

    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';', '[', ']' }

    # Define tokens
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    FOR = r'FOR'
    FUNC = r'FUNC'
    TO = r'TO'
    AND = r'AND'
    OR = r'OR'
    ARROW = r'->'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'

    EQEQ = r'=='
    NE = r'\!\='
    GT = r'\>'
    GE = r'\>\='
    LT = r'\<'
    LE = r'\<\='

    # ECHO = r'echo'
    INCREMENT = r'\+\+'
    DECREMENT = r'\-\-'

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self,t ):
        self.lineno = t.value.count('\n')

class BasicParser(Parser):
    tokens = BasicLexer.tokens

    precedence = (
        ('left', INCREMENT, DECREMENT),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),

        )

    def __init__(self):
         self.variables = { }
         self.functions = { }

    @_('')
    def statement(self, p):
        pass

    # @_('ECHO "(" expr ")"', 'ECHO "(" array ")"')
    # def statement(self, p):
    #     return ("ECHO", p[2])

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)

    @_('expr ";"')
    def statement(self, p):
        return (p.expr)

    @_('expr ";"')
    def expr(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('FOR var_assign TO expr THEN statement')
    def statement(self, p):
        return ('for_loop', ('for_loop_setup', p.var_assign, p.expr), p.statement)

    @_('IF "(" condition ")" THEN statement ELSE statement')
    def statement(self, p):
        return ('if_stmt', p.condition, ('branch', p.statement0, p.statement1))

    @_('single_con AND single_con')
    def condition(self, p):
        return 'condition_and', p.single_con0, p.single_con1

    @_('single_con OR single_con')
    def condition(self, p):
        return 'condition_or', p.single_con0, p.single_con1

    @_('single_con')
    def condition(self, p):
        return p.single_con

    @_('FUNC NAME "(" NAME ")" ARROW statement ")" ";"')
    def statement(self, p):
        return ('func_def', p.NAME0, p.NAME1, p.statement)

    @_('NAME "(" expr ")"')
    def expr(self, p):
        return ('func_call', p.NAME, p.expr)

    @_('expr INCREMENT')
    def expr(self, p):
        return ("INCREASE", p.expr)

    @_('expr DECREMENT')
    def expr(self, p):
        return ("DECREASE", p.expr)

    @_('expr EQEQ expr')
    def single_con(self, p):
        return ('condition_eqeq', p.expr0, p.expr1)

    @_('expr NE expr')
    def single_con(self, p):
        return ('condition_ne', p.expr0, p.expr1)

    @_('expr GT expr')
    def single_con(self, p):
        return ('condition_gt', p.expr0, p.expr1)

    @_('expr GE expr')
    def single_con(self, p):
        return ('condition_ge', p.expr0, p.expr1)

    @_('expr LT expr')
    def single_con(self, p):
        return ('condition_lt', p.expr0, p.expr1)

    @_('expr LE expr')
    def single_con(self, p):
        return ('condition_le', p.expr0, p.expr1)

class BasicExecute:

    def __init__(self, tree, variables, functions):
        #self.env = env
        self.variables = variables
        self.functions = functions
        result = self.walkTree(tree)
        if result is not None and isinstance(result, int):
            print(result)
        if isinstance(result, str) and result[0] == '"':
            print(result)

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'str':
            return node[1]

        if node[0] == 'INCREASE':
            temp_v = self.walkTree(node[1])
            if (type(temp_v) == int):
                self.variables[node[1][1]] = temp_v + 1
                return node[1][1]
            else:
                print(f"The value '{node[1]}' must be an integer")
                return 0

        if node[0] == 'DECREASE':
            temp_v = self.walkTree(node[1])
            if (type(temp_v) == int):
                self.variables[node[1][1]] = temp_v - 1
                return node[1][1]
            else:
                print(f"The value '{node[1]}' must be an integer")
                return 0

        if node[0] == 'if_stmt':
            result = self.walkTree(node[1])
            if node[2][0] == 'branch':
                if result:
                    return self.walkTree(node[2][1])
                return self.walkTree(node[2][2])
            else:
                if result:
                    return self.walkTree(node[2])
                return 0

        # if node[0] == 'if_stmt':
        #     result = self.walkTree(node[1])
        #     if result:
        #         return self.walkTree(node[2][1])
        #     return self.walkTree(node[2][2])

        if node[0] == 'condition_and':
            return self.walkTree(node[1]) and self.walkTree(node[2])
            
        if node[0] == 'condition_or':
            return self.walkTree(node[1]) or self.walkTree(node[2])

        if node[0] == 'condition_eqeq':
            return self.walkTree(node[1]) == self.walkTree(node[2])
            
        if node[0] == 'condition_ne':
            return self.walkTree(node[1]) != self.walkTree(node[2])

        if node[0] == 'condition_gt':
            return self.walkTree(node[1]) > self.walkTree(node[2])
            
        if node[0] == 'condition_ge':
            return self.walkTree(node[1]) >= self.walkTree(node[2])

        if node[0] == 'condition_lt':
            return self.walkTree(node[1]) < self.walkTree(node[2])
            
        if node[0] == 'condition_le':
            return self.walkTree(node[1]) <= self.walkTree(node[2])

        if node[0] == 'func_def':
            self.functions[node[1]] = (node[2], node[3])
            pass

        if node[0] == 'func_call':
            try:
                # Get node[1] (NAME) key from self.functions
                function_data = self.functions[node[1]]

                # Create temp variables for the function scope
                tempVariables = copy(self.variables)
                #print(tempVariables)
                
                tempVariables[function_data[0]] = [self.walkTree(node[2])]

                newParser = BasicExecute("()", tempVariables, self.functions)
                return newParser.walkTree(function_data[1])
            except Exception as e:
                print(e)
                pass

        # if node[0] == 'func_call':
        #     try:
        #         function = self.env[node[1]]
        #     except LookupError:
        #         print("Undefined function '%s'" % node[1])
        #         return None   
        #     functionArgs = function[1][1]
        #     args = node[2]
        #     if(len(functionArgs) != len(args)):
        #         print("Invalid argument count for function " + node[1] + ", expected " + str(len(functionArgs)) + " arguments, but got " + str(len(args)))
        #         return None

        #     newEnv = copy.deepcopy(self.env)
        #     oldEnv = self.env
        #     for i in range(len(functionArgs)):
        #         arg = self.walkTree(args[i])
        #         newEnv[functionArgs[i]] = arg
        #     self.env = newEnv
        #     returnValue = self.walkTree(function[0])
        #     self.env = oldEnv
            
        #     if(returnValue != None):
        #         return returnValue

        # if node[0] == 'func_call':
        #     try:
        #         return self.walkTree(self.env[node[1]])
        #     except LookupError:
        #         print("Undefined function '%s'" % node[1])
        #         return 0

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return int(self.walkTree(node[1]) / self.walkTree(node[2]))

        if node[0] == 'var_assign':
            self.variables[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'var':
            try:
                return self.variables[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0

        if node[0] == 'for_loop':
            if node[1][0] == 'for_loop_setup':
                loop_setup = self.walkTree(node[1])

                loop_count = self.variables[loop_setup[0]]
                loop_limit = loop_setup[1]

                for i in range(loop_count+1, loop_limit+1):
                    res = self.walkTree(node[2])
                    if res is not None:
                        print(res)
                    self.variables[loop_setup[0]] = i
                del self.variables[loop_setup[0]]

        if node[0] == 'for_loop_setup':
            return (self.walkTree(node[1]), self.walkTree(node[2]))


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    variables = { }
    functions = { }

    SIMP = BasicExecute("()", variables, functions)

    if len(sys.argv) == 2:
        f = open(sys.argv[1], "r")
        program = f.read()
        for line in program.replace("\n", "").split(";"):
            tree = parser.parse(lexer.tokenize(line))
            result = SIMP.walkTree(tree)
            if result is not None:
                resultTree = parser.parse(lexer.tokenize("printFile {0} result.txt".format(result)))
                SIMP.walkTree(resultTree)

    while True:
        try:
            text = input('SIMP > ')
        
        except EOFError:
            break
        
        if text:
            tree = parser.parse(lexer.tokenize(text))
            result = SIMP.walkTree(tree)
            if result is not None and isinstance(result, int):
                print(result)
            if isinstance(result, str) and result[0] == '"':
                print(result)
    # while True:
    #     try:
    #         text = input('basic > ')
    #     except EOFError:
    #         break
    #     if text:
    #         tree = parser.parse(lexer.tokenize(text))
    #         BasicExecute(tree, variables, functions)