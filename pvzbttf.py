from sly import Lexer, Parser
from copy import copy
import sys

class BTTFLexer(Lexer):
    tokens = { 
      IF, ELSE, 
      NAME, NUMBER, STRING,
      LT, GT, EQEQ,
      FOR, FORARROW,
      FUN,
      PRINT, PRINTFILE, FILENAME,
    }
    ignore = '\t '
    literals = { '@', '=', '+', '-', '/', 
                '*', '(', ')', ',', ';', '{', '}'}
  

    # Print
    PRINTFILE = r'printFile'
    PRINT = r'print'

    # FUN
    FUN = r'fun'

    # FOR LOOP
    FOR = r'for'
    FORARROW = r'->'

    # IF/ELSE
    IF = r'if'
    ELSE = r'else'

    # Comparators
    LT = r'<'
    GT = r'>'
    EQEQ = r'=='

    # Define tokens as regular expressions
    # (stored as raw strings)
    FILENAME = r'[a-zA-Z0-9_]*\.[a-zA-Z]*'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'
  
    # Number token
    @_(r'\d+')
    def NUMBER(self, t):
        # convert it into a python integer
        t.value = int(t.value) 
        return t
  
    # Comment token
    @_(r'//.*')
    def COMMENT(self, t):
        pass
  
    # Newline token(used only for showing
    # errors in new line)
    @_(r'\n+')
    def newline(self, t):
        self.lineno = t.value.count('\n')


class BTTFParser(Parser):
    #tokens are passed from lexer to parser
    tokens = BTTFLexer.tokens
  
    precedence = (
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

    @_('NAME "@" expr')
    def expr(self, p):
      return ('histop', p.NAME, p.expr)

    @_('IF "(" expr ")" "{" statement "}" ELSE "{" statement "}"')
    def statement(self, p):
      return ('if_else', p.expr, p.statement0, p.statement1)

    @_('IF "(" expr ")" "{" statement "}"')
    def statement(self, p):
      return ('single_if', p.expr, p.statement)

    @_('expr LT expr')
    def expr(self, p):
        return ('less_than', p.expr0, p.expr1)

    @_('expr GT expr')
    def expr(self, p):
        return ('greater_than', p.expr0, p.expr1)

    @_('expr EQEQ expr')
    def expr(self, p):
        return ('equal_equal', p.expr0, p.expr1)

    @_('FOR "(" expr FORARROW expr ")" "{" statement "}" ')
    def statement(self, p):
      return ('for_loop', p.expr0, p.expr1, p.statement)

    @_('FUN NAME "(" NAME ")" "{" statement "}"')
    def statement(self, p):
        return ('function_declaration', p.NAME0, p.NAME1, p.statement)

    @_('NAME "(" expr ")"')
    def expr(self, p):
        return ('function_call', p.NAME, p.expr)

    @_('PRINT expr')
    def statement(self, p):
        return ('print', p.expr)

    @_('PRINT statement')
    def statement(self, p):
        return ('print', p.statement)

    @_('expr "," expr')
    def expr(self, p):
        return ('arg_list', p.expr0, p.expr1)

    @_('PRINTFILE expr FILENAME')
    def expr(self, p): 
        return ('print_file', p.expr, p.FILENAME)

class BTTFExecute:    
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
        
        if node[0] == 'histop':
            try:
                return self.variables[node[1]][self.walkTree(node[2])]
            except LookupError:
                print("History lookup error, probably exceeded history range!")
                try:
                    return self.variables[node[1]][0]
                except LookupError:
                    print("Undefined variable '"+node[1]+"' found!")
                    return None

        if node[0] == 'if_else':
            if self.walkTree(node[1]):
                return self.walkTree(node[2])
            return self.walkTree(node[3])

        if node[0] == 'single_if':
            if self.walkTree(node[1]):
                return self.walkTree(node[2])
            pass

        if node[0] == 'for_loop':
            for _ in range(self.walkTree(node[1]), self.walkTree(node[2]) + 1):
                self.walkTree(node[3])

            pass

        if node[0] == 'function_declaration':
            self.functions[node[1]] = [node[2], node[3]]
            pass

        if node[0] == 'function_call':
            try:
                # Get node[1] (NAME) key from self.functions
                function_data = self.functions[node[1]]

                # Create temp variables for the function scope
                tempVariables = copy(self.variables)
                # print(tempVariables)
                
                tempVariables[function_data[0]] = [self.walkTree(node[2])]

                newParser = BTTFExecute("()", tempVariables, self.functions)
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
    lexer = BTTFLexer()
    parser = BTTFParser()
    variables = {}
    functions = {}
      
    BTTF = BTTFExecute("()", variables, functions)

    if len(sys.argv) == 2:
        f = open(sys.argv[1], "r")
        program = f.read()
        for line in program.replace("\n", "").split(";"):
            tree = parser.parse(lexer.tokenize(line))
            result = BTTF.walkTree(tree)
            if result is not None:
                resultTree = parser.parse(lexer.tokenize("printFile {0} result.txt".format(result)))
                BTTF.walkTree(resultTree)

    while True:
        try:
            text = input('BTTF > ')
        
        except EOFError:
            break
        
        if text:
            tree = parser.parse(lexer.tokenize(text))
            result = BTTF.walkTree(tree)
            if result is not None and isinstance(result, int):
                print(result)
            if isinstance(result, str) and result[0] == '"':
                print(result)