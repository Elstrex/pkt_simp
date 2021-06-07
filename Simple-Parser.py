from sly import Lexer
from sly import Parser
from copy import copy

class SIMPLexer(Lexer):
    tokens = { IF, THEN, ELSE, NAME, NUMBER, STRING, FOR, TO, END, ARROW, FUNC, PRINT, PRINTF, FILENAME, EQEQ, NE, GT, LT, INCREMENT, DECREMENT, AND }
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
    AND = r'AND'

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
    
    @_('FOR "(" expr TO expr ")" THEN statement AND statement AND statement END')
    def statement(self, p):
      return ('for_loop_3', p.expr0, p.expr1, p.statement0, p.statement1, p.statement2)

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

if __name__ == '__main__':
    lexer = SIMPLexer()
    parser = SIMPParser()
    variables = {}
    functions ={}
    while True:
        try:
            text = input('simp > ')
        except EOFError:
            break
        if text:
            tree = parser.parse(lexer.tokenize(text))
            print(tree)