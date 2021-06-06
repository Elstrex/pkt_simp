from sly import Lexer, Parser


class SLYLexer(Lexer):
    tokens = {TYPE, NAME, PRINT, FILEPRINT,  COUNTER, C1, C2, NUM, STR, CHR, ADDN, MULTN, MINN, DIVN,
              BEGIN, END, IF, ELSE, FOR, WHILE,
              EQEQ, LT, LE, GT, GE, NE, AND, OR, INCR, DECR, VOID, RETURN}
    ignore = ' \t'
    literals = {'=', '+', '-', '*', '/', '(', ')', ';', '.', ',', '[', ']'}

    # Tokens
    TYPE = r'(num)|(str)|(chr)'
    IF = r'if'
    ELSE = r'else'
    FOR = r'for'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    AND = r'&&'
    OR = r'\|\|'
    NE = r'!='
    EQEQ = r'=='
    COUNTER = r'::'
    C1 = r'c1'
    C2 = r'c2'
    FILEPRINT = r'fileprint'
    PRINT = r'print'
    WHILE = r'while'
    INCR = r'\+\+'
    ADDN = r'\+\='
    MULTN = r'\*\='
    MINN = r'\-\='
    DIVN = r'\/\='
    DECR = r'\-\-'
    VOID = r'void'
    RETURN = r'return'

    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'

    BEGIN = r'\{'
    END = r'\}'

    @_(r'\d+')
    def NUM(self, t):
        t.value = int(t.value)
        return t

    @_(r'\".*?\"')
    def STR(self, t):
        t.value = t.value.strip("\"")
        return t

    @_(r'\'.*?\'')
    def CHR(self, t):
        if (len(t.value) != 3):
            print(f"Bad input at line {self.lineno}")
            return None
        t.value = t.value[1]
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1


class SLYParser(Parser):
    tokens = SLYLexer.tokens
    debugfile = 'parser.out'

    precedence = (
        ('left', AND, OR),
        ('left', EQEQ, NE, LT, LE, GT, GE, INCR, DECR),
        ('left', '+', '-', ADDN, MINN),
        ('left', '*', '/', MULTN, DIVN),
        ('right', 'UMINUS'),
    )

    @_('statements statement')
    def statements(self, p):
        return [p[0], p[1]]

    @_('RETURN statement')
    def statements(self, p):
        return [0, ("RETURN", p[1])]

    @_('statements RETURN statement')
    def statements(self, p):
        return [p[0], ("RETURN", p[2])]

    @_('statement')
    def statements(self, p):
        return [p[0], 0]

    @_('PRINT "(" expr ")"', 'PRINT "(" array ")"')
    def statement(self, p):
        return ("PRINT", p[2])

    @_('positional_args')
    def args(self, p):
        return ("args", p.positional_args)

    @_('funcion_declare')
    def statement(self, p):
        return p.funcion_declare

    @_('funcion_call')
    def statement(self, p):
        return p.funcion_call

    @_('VOID NAME "(" args ")" BEGIN statements END', 'TYPE NAME "(" args ")" BEGIN statements END')
    def funcion_declare(self, p):
        return ("FUNC_DECLARE",  p.NAME, p.args, p[6])

    @_("positional_args ',' pos_args")
    def positional_args(self, p):
        return p.positional_args + (p.pos_args,)

    @_("pos_args")
    def positional_args(self, p):
        return (p.pos_args,)

    @_("NAME")
    def pos_args(self, p):
        return p.NAME

    @_('NAME "(" args ")"')
    def funcion_call(self, p):
        return ("FUNC_CALL", p.NAME, p.args)

    @_('TYPE NAME "=" funcion_call')
    def statement(self, p):
        return ("VAR_ASSIGN", p.TYPE, p.NAME, p.funcion_call)

    @_('PRINT "(" var_func ")"')
    def statement(self, p):
        return ("PRINT_C", p.var_func)

    @_('FILEPRINT "(" expr "," expr ")"', 'FILEPRINT "(" expr "," array ")"')
    def statement(self, p):
        return ("FILEPRINT", p[2], p[4])

    @_('FILEPRINT "(" expr "," var_func ")"')
    def statement(self, p):
        return ("FILEPRINT_C", p[2], p.var_func)

    @_('NAME "." C1',
       'NAME "." C2')
    def var_func(self, p):
        return ('VAR_FUNC', p.NAME, p[2])

    @_('array "." C1',
       'array "." C2')
    def var_func(self, p):
        return ('VAR_FUNC', p.array, p[2])

    @_("var_assign", "expr", "array")
    def statement(self, p):
        return p[0]

    @_('TYPE NAME "=" expr')
    def var_assign(self, p):
        return ("VAR_ASSIGN", p.TYPE, p.NAME, p.expr)

    @_('array "=" expr')
    def var_assign(self, p):
        return ("VAR_ASSIGN", None, p.array, p.expr)

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ("VAR_ASSIGN", None, p.NAME, p.expr)

    @_('NAME "=" array')
    def var_assign(self, p):
        return ("VAR_ASSIGN", None, p.NAME, p.array)

    @_('TYPE NAME "=" array')
    def var_assign(self, p):
        return ("VAR_ASSIGN", p.TYPE, p.NAME, p.array)

    @_('TYPE NAME "=" array COUNTER')
    def var_assign(self, p):
        return ("VAR_ASSIGN", p.TYPE, p.NAME, p.array, 0, 0)

    @_('TYPE NAME "=" expr COUNTER')
    def var_assign(self, p):
        return ("VAR_ASSIGN", p.TYPE, p.NAME, p.expr, 0, 0)

    @_('expr INCR')
    def expr(self, p):
        return ("INCREASE", p.expr)

    @_('expr DECR')
    def expr(self, p):
        return ("DECREASE", p.expr)

    @_('expr ADDN expr')
    def expr(self, p):
        return ("ADDN", p.expr0, p.expr1)

    @_('expr MINN expr')
    def expr(self, p):
        return ("MINN", p.expr0, p.expr1)

    @_('expr MULTN expr')
    def expr(self, p):
        return ("MULTN", p.expr0, p.expr1)

    @_('expr DIVN expr')
    def expr(self, p):
        return ("DIVN", p.expr0, p.expr1)

    @_('expr "+" expr', 'funcion_call "+" funcion_call')
    def expr(self, p):
        return ("ADD", p[0], p[2])

    @_('expr "-" expr')
    def expr(self, p):
        return ("SUB", p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ("MUL", p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ("DIV", p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ("NEG", p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('expr EQEQ expr')
    def expr(self, p):
        return ("EQEQ", p.expr0, p.expr1)

    @_('expr NE expr')
    def expr(self, p):
        return ("NE", p.expr0, p.expr1)

    @_('expr LT expr')
    def expr(self, p):
        return ("LT", p.expr0, p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        return ("LE", p.expr0, p.expr1)

    @_('expr GT expr')
    def expr(self, p):
        return ("GT", p.expr0, p.expr1)

    @_('expr GE expr')
    def expr(self, p):
        return ("GE", p.expr0, p.expr1)

    @_('expr AND expr')
    def expr(self, p):
        return ("AND", p.expr0, p.expr1)

    @_('expr OR expr')
    def expr(self, p):
        return ("OR", p.expr0, p.expr1)

    @_('NUM')
    def expr(self, p):
        return ("NUM", p.NUM)

    @_('STR')
    def expr(self, p):
        return ("STR", p.STR)

    @_('CHR')
    def expr(self, p):
        return ("CHR", p.CHR)

    @_('conditional')
    def statement(self, p):
        return p[0]

    @_("IF expr statements")
    def conditional(self, p):
        return ("IF", p.expr, p.statements)

    @_("IF expr BEGIN statements END")
    def conditional(self, p):
        return ("IF", p.expr, p.statements)

    @_("IF expr statements ELSE statements")
    def conditional(self, p):
        return ("IF", p.expr, ('branch', p.statements0,  p.statements1))

    @_("IF expr BEGIN statements END ELSE BEGIN statements END")
    def conditional(self, p):
        return ("IF", p.expr, ('branch',  p.statements0,  p.statements1))

    @_('FOR "(" var_assign ";" expr ";" expr ")" BEGIN statements END')
    def statement(self, p):
        return ('FOR', p.var_assign, p.expr0, p.expr1,  p.statements)

    @_('WHILE "(" expr ")" BEGIN statements END')
    def statement(self, p):
        return ('WHILE', p.expr, p.statements, p.lineno)

    @_('"[" elements "]"')
    def array(self, p):
        return ("ARRAY", p.elements)

    @_('statement')
    def elements(self, p):
        return [p.statement]

    @_('statement "," elements')
    def elements(self, p):
        return [p.statement] + p.elements

    @_('NAME "[" expr "]"')
    def array(self, p):
        return ('VAR_INDEX', ('VAR', p.NAME), p.expr)

    @_('NAME')
    def expr(self, p):
        return ('VAR', p.NAME)


class SLYInterpreter:
    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)

    def walkTree(self, node):
        if isinstance(node, int):
            return node

        if isinstance(node, str):
            return node

        if node is None:
            return None

        if isinstance(node, list):
            res = self.walkTree(node[0])
            if(isinstance(res, tuple) and res[0] == "return"):
                return res
            return self.walkTree(node[1])

        if node[0] == 'FUNC_DECLARE':
            funcName = node[1]
            args = node[2]
            funcInside = node[3]
            self.env[funcName] = (args, funcInside)

        if node[0] == 'RETURN':
            return ("return", self.walkTree(node[1]))

        if node[0] == 'FUNC_CALL':
            varCopy = self.env.copy()

            for x in range(len(node[2][1])):
                self.env[self.env[node[1]][0][1][x]] = self.env[node[2][1][x]]

            func = self.env[node[1]]
            if len(func[0][1]) - 1 != len(node[2][1])-1:
                print("Argument count doesn't match!")
                print(
                    f"Function has {len(func[1])-1}, call has {len(node[2])-1}")
                return 0

            res = self.walkTree(func[1])

            for var in self.env.copy():
                if var not in varCopy:
                    del self.env[var]
                if var in varCopy:
                    self.env[var] = varCopy[var]
            if(res[0] == "return"):
                return res[1]

        if node[0] == 'NUM' or node[0] == 'STR' or node[0] == 'CHR':
            return node[1]

        if node[0] == 'ARRAY':
            temp = []
            for e in node[1]:
                temp.append(self.walkTree(e))
            return temp

        if node[0] == 'VAR_INDEX':
            array = self.walkTree(node[1])
            index = self.walkTree(node[2])

            if (len(array) <= index):
                print("Index was outside the bounds of the array")
                return 0

            if isinstance(array[0], tuple) and len(array[0]) > 1:
                array[index] = (array[index][0], array[index]
                                [1] + 1, array[index][2])
                self.env[node[1][1]] = array

            return array[index]

        if node[0] == 'IF':
            result = self.walkTree(node[1])
            if node[2][0] == 'branch':
                if result:
                    return self.walkTree(node[2][1])
                return self.walkTree(node[2][2])
            else:
                if result:
                    return self.walkTree(node[2])
                return 0

        if node[0] == "FOR":
            varCopy = self.env.copy()
            init = self.walkTree(node[1])
            if init == 0:
                return 0
            init = self.env[init]
            condition = self.walkTree(node[2])

            while condition:
                self.walkTree(node[4])
                self.walkTree(node[3])
                condition = self.walkTree(node[2])

            del self.env[self.walkTree(node[1])]
            for var in self.env.copy():
                if var not in varCopy:
                    del self.env[var]
# ------------------------------------------------------------------------------

        if node[0] == 'ADDN':
            temp_v1 = self.walkTree(node[1])
            temp_v2 = self.walkTree(node[2])
            if (type(temp_v1) == int and type(temp_v2) == int):
                self.env[node[1][1]] = temp_v1 + temp_v2
                return node[1][1]
            else:
                print(f"Both values must be an integers")
                return 0

        if node[0] == 'MINN':
            temp_v1 = self.walkTree(node[1])
            temp_v2 = self.walkTree(node[2])
            if (type(temp_v1) == int and type(temp_v2) == int):
                self.env[node[1][1]] = temp_v1 - temp_v2
                return node[1][1]
            else:
                print(f"Both values must be an integers")
                return 0

        if node[0] == 'MULTN':
            temp_v1 = self.walkTree(node[1])
            temp_v2 = self.walkTree(node[2])
            if (type(temp_v1) == int and type(temp_v2) == int):
                self.env[node[1][1]] = temp_v1 * temp_v2
                return node[1][1]
            else:
                print(f"Both values must be an integers")
                return 0

        if node[0] == 'DIVN':
            temp_v1 = self.walkTree(node[1])
            temp_v2 = self.walkTree(node[2])
            if (type(temp_v1) == int and type(temp_v2) == int):
                self.env[node[1][1]] = (int)(temp_v1 / temp_v2)
                return node[1][1]
            else:
                print(f"Both values must be an integers")
                return 0

        if node[0] == 'INCREASE':
            temp_v = self.walkTree(node[1])
            if (type(temp_v) == int):
                self.env[node[1][1]] = temp_v + 1
                return node[1][1]
            else:
                print(f"The value '{node[1]}' must be an integer")
                return 0

        if node[0] == 'DECREASE':
            temp_v = self.walkTree(node[1])
            if (type(temp_v) == int):
                self.env[node[1][1]] = temp_v - 1
                return node[1][1]
            else:
                print(f"The value '{node[1]}' must be an integer")
                return 0
# ------------------------------------------------------------------------------

        if node[0] == "AND":
            return self.walkTree(node[1]) and self.walkTree(node[2])

        if node[0] == "OR":
            return self.walkTree(node[1]) or self.walkTree(node[2])

        if node[0] == 'ADD':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'SUB':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'MUL':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'DIV':
            return self.walkTree(node[1]) / self.walkTree(node[2])
        elif node[0] == 'EQEQ':
            return self.walkTree(node[1]) == self.walkTree(node[2])
        elif node[0] == 'NE':
            return self.walkTree(node[1]) != self.walkTree(node[2])
        elif node[0] == 'LT':
            return self.walkTree(node[1]) < self.walkTree(node[2])
        elif node[0] == 'LE':
            return self.walkTree(node[1]) <= self.walkTree(node[2])
        elif node[0] == 'GT':
            return self.walkTree(node[1]) > self.walkTree(node[2])
        elif node[0] == 'GE':
            return self.walkTree(node[1]) >= self.walkTree(node[2])

        if node[0] == 'VAR_ASSIGN':

            if node[1] is None and node[2] not in self.env and node[2][0].lower() != "var_index":
                print(
                    f"The name '{node[2]}' does not exist in the current context")
                return 0
            if node[1] is not None and node[3][0].lower() != "array" and node[3][
                    0].lower() != "var_index" and node[3][0] != "FUNC_CALL" and node[3][0] != "VAR":
                res = self.walkTree(node[3])
                dataType = ""
                if (type(res) == int):
                    dataType = "num"
                elif (res.isalpha()):
                    dataType = "chr"
                if (type(res) == str):
                    dataType = "str"
                if dataType != node[1]:
                    print(
                        f"Cannot implicitly convert type {dataType} to {node[1] }")
                    return 0

            if node[1] is None and node[2][0].lower() == "var_index":
                dataType = ""
                dataType2 = ""
                res = self.walkTree(node[2][1])
                if (isinstance(res[0], tuple)):
                    if (type(res[0][0]) == int):
                        dataType = "num"
                    elif (res[0][0].isalpha()):
                        dataType = "chr"
                    if (type(res[0][0]) == str):
                        dataType = "str"
                else:
                    if (type(res[0]) == int):
                        dataType = "num"
                    elif (res[0].isalpha()):
                        dataType = "chr"
                    if (type(res[0]) == str):
                        dataType = "str"
                res2 = self.walkTree(node[3])

                if (type(res2) == int):
                    dataType2 = "num"
                elif (res2.isalpha()):
                    dataType2 = "chr"
                if (type(res2) == str):
                    dataType2 = "str"

                if dataType != dataType2:
                    print(
                        f"Cannot implicitly convert type {dataType2} to {dataType}")
                    return 0

            if node[3][0].lower() == "array":
                for val in node[3][1]:
                    if (val[0].lower() != node[1]):
                        print(
                            f"Array contains different value data types {val[0].lower()} than declaration {node[1]}")
                        return 0
            if node[len(node) - 1] == 0:
                if node[3][0] == "ARRAY":
                    array = self.walkTree(node[3])
                    i = 0
                    for val in array.copy():
                        array[i] = (val, 0, 0)
                        i += 1
                    self.env[node[2]] = array
                    return node[2]
                self.env[node[2]] = (self.walkTree(node[3]), 0, 0)
                return node[2]
            elif node[2] in self.env:
                if isinstance(self.env[node[2]], tuple) and len(self.env[node[2]]) > 1:
                    self.env[node[2]] = (self.walkTree(
                        node[3]), self.env[node[2]][1], self.env[node[2]][2] + 1)
                    return node[2]
            elif node[2][0] == "VAR_INDEX" and node[2][1][1] in self.env:
                if isinstance(self.env[node[2][1][1]], list) and len(self.env[node[2][1][1]]) > 1:
                    array = self.walkTree(node[2][1])
                    index = self.walkTree(node[2][2])
                    if len(array) <= index:
                        print("Index was outside the bounds of the array")
                        return 0
                    if isinstance(array[index], tuple):
                        array[index] = (self.walkTree(node[3]),
                                        array[index][1], array[index][2] + 1)
                    else:
                        array[index] = self.walkTree(node[3])
                    self.env[node[2][1][1]] = array
                    return node[2]

            if node[1] is not None and node[3][0] == "FUNC_CALL":
                res = self.walkTree(node[3])
                dataType = ""
                if (type(res) == int):
                    dataType = "num"
                elif (res.isalpha()):
                    dataType = "chr"
                if (type(res) == str):
                    dataType = "str"
                if dataType != node[1]:
                    print(
                        f"Cannot implicitly convert type {dataType} to {node[1] }")
                    return 0
                self.env[node[2]] = res
                return node[2]

            self.env[node[2]] = self.walkTree(node[3])
            return node[2]

        if node[0] == 'VAR':

            try:
                if node[1] in self.env and isinstance(self.env[node[1]], tuple) and len(self.env[node[1]]) > 2:
                    self.env[node[1]] = (
                        self.env[node[1]][0], self.env[node[1]][1] + 1, self.env[node[1]][2])
                    return self.env[node[1]][0]
                return self.env[node[1]]
            except:
                print("Undefined variable '" + node[1] + "' found!")
                return 0

        if (node[0] == 'WHILE'):
            varCopy = self.env.copy()
            condition = self.walkTree(node[1])
            while condition:
                self.walkTree(node[2])
                condition = self.walkTree(node[1])
            for var in self.env.copy():
                if var not in varCopy:
                    del self.env[var]

        if node[0] == 'FILEPRINT':
            if node[1][0] != "STR":
                print("First inptu field must be file name!")
                return 0
            f = open(node[1][1], "w")

            if node[2][0] == "STR" or node[2][0] == "NUM" or node[2][0] == "CHR":
                f.write(node[2][1])
                f.close()
                return 0

            if node[2][0] == 'VAR':
                try:
                    if isinstance(self.env[node[2][1]], tuple) and len(self.env[node[2][1]]) > 1:
                        self.env[node[2][1]] = (
                            self.env[node[2][1]][0], self.env[node[2][1]][1] + 1, self.env[node[2][1]][2])
                        temp = self.env[node[2][1]][0]
                        f.write(str(temp))
                        f.close()
                    else:
                        if isinstance(self.env[node[2][1]], list) and isinstance(self.env[node[2][1]][0],
                                                                                 tuple) and len(
                                self.env[node[2][1]][0]) > 1:
                            arr = []
                            for val in self.env[node[2][1]]:
                                arr.append(val[0])
                            f.write(str(arr))
                            f.close()
                            return
                        temp = self.env[node[2][1]]
                        f.write(str(temp))
                        f.close()

                except:
                    print("Undefined variable '" + node[2][1] + "' found!")
                    return 0

            if node[2][0] == 'VAR_INDEX':
                try:
                    res = self.walkTree(node[2])
                    if isinstance(res, tuple) and len(res) > 1:
                        f.write(res[0])
                        f.close()
                        return
                    f.write(res)
                    f.close()
                except:
                    print("Undefined variable '" + node[2][1] + "' found!")
                    return 0

        if node[0] == 'FILEPRINT_C':
            if node[1][0] != "STR":
                print("First inptu field must be file name!")
                return 0
            f = open(node[1][1], "w")
            try:
                if node[2][1][0] != 'VAR_INDEX' and isinstance(self.env[node[2][1]], list):
                    if node[2][2] == 'c1':
                        arr = []
                        for val in self.env[node[2][1]]:
                            arr.append(val[0:2])
                        f.write(str(arr))
                        f.close()
                        return
                    if node[2][2] == 'c2':
                        arr = []
                        for val in self.env[node[2][1]]:
                            arr.append(val[0:3:2])
                        f.write(str(arr))
                        f.close()
                        return
                    return

                if node[2][1][0] == "VAR_INDEX":
                    val = self.env[node[2][1][1][1]][node[2][1][2][1]]
                    if node[2][2] == 'c1':
                        f.write(str(val[1]))
                        f.close()
                    if node[2][2] == 'c2':
                        f.write(str(val[2]))
                        f.close()
                    return
                if node[2][2] == 'c1':
                    print(self.env[node[2][1]][1])
                    f.write(str(self.env[node[2][1]][1]))
                    f.close()
                if node[2][2] == 'c2':
                    f.write(str(self.env[node[2][1]][2]))
                    f.close()
            except:
                print("Variable '" + node[2][1] + "' doesn't have counter!")
                return 0

        if node[0] == 'PRINT':
            if node[1][0] == "STR" or node[1][0] == "NUM" or node[1][0] == "CHR":
                print(node[1][1])

            if node[1][0] == 'VAR':
                try:
                    if isinstance(self.env[node[1][1]], tuple) and len(self.env[node[1][1]]) > 1:
                        self.env[node[1][1]] = (
                            self.env[node[1][1]][0], self.env[node[1][1]][1] + 1, self.env[node[1][1]][2])
                        print(self.env[node[1][1]][0])
                    else:
                        if isinstance(self.env[node[1][1]], list) and isinstance(self.env[node[1][1]][0],
                                                                                 tuple) and len(
                                self.env[node[1][1]][0]) > 1:
                            arr = []
                            for val in self.env[node[1][1]]:
                                arr.append(val[0])
                            print(arr)
                            return
                        print(self.env[node[1][1]])

                except:
                    print("Undefined variable '" + node[1][1] + "' found!")
                    return 0

            if node[1][0] == 'VAR_INDEX':
                try:
                    res = self.walkTree(node[1])
                    if isinstance(res, tuple) and len(res) > 1:
                        print(res[0])
                        return
                    print(res)
                except:
                    print("Undefined variable '" + node[1][1] + "' found!")
                    return 0

        if node[0] == 'PRINT_C':
            try:
                if node[1][1][0] != 'VAR_INDEX' and isinstance(self.env[node[1][1]], list):
                    if node[1][2] == 'c1':
                        arr = []
                        for val in self.env[node[1][1]]:
                            arr.append(val[0:2])
                        print(arr)
                        return
                    if node[1][2] == 'c2':
                        arr = []
                        for val in self.env[node[1][1]]:
                            arr.append(val[0:3:2])
                        print(arr)
                        return
                    return

                if node[1][1][0] == "VAR_INDEX":
                    val = self.env[node[1][1][1][1]][node[1][1][2][1]]
                    if node[1][2] == 'c1':
                        print(val[1])
                    if node[1][2] == 'c2':
                        print(val[2])
                    return
                if node[1][2] == 'c1':
                    print(self.env[node[1][1]][1])
                if node[1][2] == 'c2':
                    print(self.env[node[1][1]][2])
            except:
                print("Variable '" + node[1][1] + "' doesn't have counter!")
                return 0


def main():
    lexer = SLYLexer()
    parser = SLYParser()
    env = {}
    while True:
        file: str = input("Enter file name ")
        try:
            fd = open(file, encoding='UTF-8').read()
            tree = parser.parse(lexer.tokenize(fd))
            # print(tree)
            SLYInterpreter(tree, env)
            break
        except:
            print(f'The specified file "{file}" was not found!')
    main()


if __name__ == '__main__':
    main()
