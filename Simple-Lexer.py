from sly import Lexer

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




if __name__ == '__main__':
    lexer = SIMPLexer()
    env = {}
    while True:
        try:
            text = input('simp > ')
        except EOFError:
            break
        if text:
            lex = lexer.tokenize(text)
            for token in lex:
                print(token)