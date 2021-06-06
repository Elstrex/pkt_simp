from sly import Lexer
from sly import Parser

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
        self.env = { }

    @_('')
    def statement(self, p):
        pass

    # @_('ECHO "(" expr ")"', 'ECHO "(" array ")"')
    # def statement(self, p):
    #     return ("ECHO", p[2])

    @_('FOR var_assign TO expr THEN statement ";"')
    def statement(self, p):
        return ('for_loop', ('for_loop_setup', p.var_assign, p.expr), p.statement)

    @_('IF "(" condition ")" THEN statement ELSE statement ";"')
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

    @_('FUNC NAME "(" ")" ARROW statement ";"')
    def statement(self, p):
        return ('func_def', p.NAME, p.statement)

    @_('NAME "(" ")"')
    def statement(self, p):
        return ('func_call', p.NAME)

    @_('expr INCREMENT ";"')
    def expr(self, p):
        return ("INCREASE", p.expr)

    @_('expr DECREMENT ";"')
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

    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr ";"')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME "=" STRING ";"')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING)

    @_('expr ";"')
    def statement(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr ";"')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr ";"')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr ";"')
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



if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    env = {}
    while True:
        try:
            text = input('basic > ')
        except EOFError:
            break
        if text:
            tree = parser.parse(lexer.tokenize(text))
            print(tree)