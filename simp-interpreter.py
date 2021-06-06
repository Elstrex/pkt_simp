from sly import Lexer
from sly import Parser
from copy import copy
import sys

class SIMPLexer(Lexer):
    tokens = { IF, THEN, ELSE, NAME, NUMBER, STRING, FOR, TO, END, ARROW, FUNC, PRINT, PRINTF, FILENAME, EQEQ, NE, GT, LT, INCREMENT, DECREMENT, RETURN }
    ignore = '\t '
    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';', '{', '}', '[', ']'}
  
    PRINTF = r'printf'
    PRINT = r'print'
    FUNC = r'FUNC'
    FOR = r'FOR'
    TO = r'TO'
    END = r'END'
    ARROW = r'->'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'
    RETURN = r'RETURN'

    EQEQ = r'\=\='
    NE = r'\!\='
    GT = r'\>'
    LT = r'\<'
    INCREMENT = r'\+\+'
    DECREMENT = r'\-\-'

    FILENAME = r'[a-zA-Z0-9_]*\.[a-zA-Z]*'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'
  
    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value) 
        return t
  
    @_(r'/!.*')
    def COMMENT(self, t):
        pass
  
    @_(r'\n+')
    def newline(self, t):
        self.lineno = t.value.count('\n')


class SIMPParser(Parser):
    tokens = SIMPLexer.tokens
  
    precedence = (
        ('left', INCREMENT, DECREMENT),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', ','),
        ('right', 'UMINUS'),
    )
  
    def __init__(self):
        self.variables = { }
        self.functions = { }
  
    @_('')
    def statement(self, p):
        pass
  
    @_('var_assign')
    def statement(self, p):
        return p.var_assign
  
    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)
  
    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)
  
    @_('expr')
    def statement(self, p):
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

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)

    @_('expr INCREMENT')
    def expr(self, p):
        return ("INCREASE", p.expr)

    @_('expr DECREMENT')
    def expr(self, p):
        return ("DECREASE", p.expr)

    @_('IF "(" expr ")" THEN statement ELSE statement END')
    def statement(self, p):
      return ('if_stmt', p.expr, p.statement0, p.statement1)

    @_('expr LT expr')
    def expr(self, p):
        return ('less_than', p.expr0, p.expr1)   

    @_('expr GT expr')
    def expr(self, p):
        return ('greater_than', p.expr0, p.expr1)

    @_('expr EQEQ expr')
    def expr(self, p):
        return ('equal_equal', p.expr0, p.expr1)

    @_('expr NE expr')
    def expr(self, p):
        return ('not_equal', p.expr0, p.expr1)

    @_('FOR "(" expr TO expr ")" THEN statement END')
    def statement(self, p):
      return ('for_loop', p.expr0, p.expr1, p.statement)

    @_('FUNC NAME "(" NAME ")" ARROW statement END')
    def statement(self, p):
        return ('func_def', p.NAME0, p.NAME1, p.statement)

    @_('NAME "(" expr ")"')
    def expr(self, p):
        return ('func_call', p.NAME, p.expr)

    @_('PRINT expr')
    def statement(self, p):
        return ('print', p.expr)

    @_('PRINT statement')
    def statement(self, p):
        return ('print', p.statement)

    @_('expr "," expr')
    def expr(self, p):
        return ('arg_list', p.expr0, p.expr1)

    # @_('RETURN "(" statement ")"')
    # def statement(self, p):
    #     return [0, ("RETURN", p[1])]

    # @_('statements RETURN statement')
    # def statements(self, p):
    #     return [p[0], ("RETURN", p[2])]

    @_('PRINTF expr FILENAME')
    def expr(self, p): 
        return ('print_file', p.expr, p.FILENAME)

class SIMPExecute:    
    def __init__(self, tree, variables, functions):
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
  
        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])

        if node[0] == 'less_than':
            return self.walkTree(node[1]) < self.walkTree(node[2])
        elif node[0] == 'greater_than':
            return self.walkTree(node[1]) > self.walkTree(node[2])
        elif node[0] == 'equal_equal':
            return self.walkTree(node[1]) == self.walkTree(node[2])
        elif node[0] == 'not_equal':
            return self.walkTree(node[1]) != self.walkTree(node[2])
  
        if node[0] == 'var_assign':
            try:
              self.variables[node[1]] = [self.walkTree(node[2])] + self.variables[node[1]]
            except:
              self.variables[node[1]] = [self.walkTree(node[2])]

            return node[1]
  
        if node[0] == 'var':
            try:
                return self.variables[node[1]][0]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0

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
            if self.walkTree(node[1]):
                return self.walkTree(node[2])
            return self.walkTree(node[3])

        if node[0] == 'for_loop':
            for _ in range(self.walkTree(node[1]), self.walkTree(node[2]) + 1):
                self.walkTree(node[3])

            pass

        if node[0] == 'func_def':
            self.functions[node[1]] = [node[2], node[3]]
            pass

        # if node[0] == 'return':
        #     return ("RETURN", self.walkTree(node[2]))

        if node[0] == 'func_call':
            try:
                function_data = self.functions[node[1]]
                tempVariables = copy(self.variables)     
                tempVariables[function_data[0]] = [self.walkTree(node[2])]
                newParser = SIMPExecute("()", tempVariables, self.functions)
                return newParser.walkTree(function_data[1])
            except Exception as e:
                print(e)
                pass

        if node[0] == 'print':
            print(self.walkTree(node[1]))
            pass

        if node[0] == 'print_file':
            f = open(node[2], "w+")
            f.write(str(self.walkTree(node[1])))

if __name__ == '__main__':
    lexer = SIMPLexer()
    parser = SIMPParser()
    variables = {}
    functions = {}
      
    SIMP = SIMPExecute("()", variables, functions)

    if len(sys.argv) == 2:
        f = open(sys.argv[1], "r")
        program = f.read()
        for line in program.replace("\n", "").split(";"):
            tree = parser.parse(lexer.tokenize(line))
            result = SIMP.walkTree(tree)
            if result is not None:
                resultTree = parser.parse(lexer.tokenize("printf {0} result.txt".format(result)))
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

                