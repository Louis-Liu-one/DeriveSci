
from textwrap import indent  # 调试用

import re
import types
import operator
import functools
import sympy as sp
from pyparsing import Literal, Suppress, Word, Regex
from pyparsing import Forward, Opt, ZeroOrMore, OneOrMore
from pyparsing import identchars, identbodychars
from pyparsing import ParserElement, ParseException


__all__ = ['fpparse', 'fpeval', 'ParseException']

sp.init_printing()                                 # 调试用
indent = functools.partial(indent, prefix='    ')  # 调试用

_function_type = type | types.FunctionType | types.MethodType \
    | types.MethodDescriptorType | sp.FunctionClass
ParserElement.enable_packrat()


def _update_funceval(ns, funceval):
    ns.update({'eval': funceval})


def _as_sympy(obj):
    if isinstance(obj, list):
        return sp.Array(obj)
    elif isinstance(obj, set | tuple | dict | int | float | complex):
        return sp.sympify(obj)
    return sp.nan if obj is None else obj


def _as_fpelement(obj):
    if isinstance(obj, FPElement):
        return obj
    return FPExpression(_as_sympy(obj))


def _ident2symbol(ident):
    if isinstance(ident, _function_type):
        return sp.Symbol(ident.__name__)
    return sp.Symbol(str(ident))


class Context:
    '''程序变量作用域。'''

    def __init__(self, master=None, context=None):
        self.context = {} if context is None else context
        self.master = master
        self.globals, self.nonlocals = set(), set()

    def __contains__(self, identifier):
        if isinstance(identifier, str):
            identifier = sp.Symbol(identifier)
        return identifier in self.globals or identifier in self.nonlocals \
            or identifier in self.context \
            or self.master is not None and identifier in self.master

    def __getitem__(self, identifier):
        if isinstance(identifier, str):
            identifier = sp.Symbol(identifier)
        if identifier in self.globals:
            if self.master is not None:
                self.context[identifier] = self.master[identifier]
                return self.context[identifier]
            elif identifier in self.context:
                return self.context[identifier]
            return identifier
        elif identifier in self.nonlocals:
            return self.master[identifier]
        elif identifier in self.context:
            return self.context[identifier]
        elif self.master is None:
            return identifier
        return self.master[identifier]

    def __setitem__(self, identifier, value):
        if isinstance(identifier, str):
            identifier = sp.Symbol(identifier)
        if identifier in self.globals:
            self.context[identifier] = value
            if self.master is not None:
                self.master[identifier] = value
        elif identifier in self.nonlocals:
            self.master[identifier] = value
        else:
            self.context[identifier] = value

    def add_nonlocal(self, identifier):
        if isinstance(identifier, str):
            identifier = sp.Symbol(identifier)
        if identifier in self.context:
            raise SyntaxError(
                f"name '{identifier}' is assigned to"
                " before nonlocal declaration")
        elif self.master is None:
            raise SyntaxError(
                'nonlocal declaration not allowed at module level')
        elif identifier not in self.master:
            raise SyntaxError(f"no binding for nonlocal '{identifier}' found")
        self.nonlocals.add(identifier)

    def _add_global(self, identifier):
        if isinstance(identifier, str):
            identifier = sp.Symbol(identifier)
        self.globals.add(identifier)
        if self.master is not None:
            self.master._add_global(identifier)

    def add_global(self, identifier):
        if identifier in self.context:
            raise SyntaxError(
                f"name '{identifier}' is assigned to"
                " before global declaration")
        self._add_global(identifier)


class ProgramStack:
    '''程序调用栈。'''

    def __init__(self, context=None):
        self.stack = [Context(context=context)]

    def current_context(self):
        return self.stack[-1]

    def __getitem__(self, identifier):
        return self.current_context()[identifier]

    def __setitem__(self, identifier, value):
        self.current_context()[identifier] = value

    def add_globals(self, identifiers):
        for identifier in identifiers:
            self.current_context().add_global(identifier)

    def add_nonlocals(self, identifiers):
        for identifier in identifiers:
            self.current_context().add_nonlocal(identifier)

    def add_context(self, context=None):
        self.stack.append(Context(self.current_context(), context=context))

    def pop_context(self):
        if len(self.stack) == 1:
            raise IndexError('cannot pop the main context')
        return self.stack.pop()


class FPSliceList:

    def __init__(self, slices):
        self.slices = tuple(slices)


class FPElement:
    '''一切语法树结点的基类。

    语法树求值之前必须调用`setup_stack()`初始化调用栈。
    '''

    def __init__(self, children=None):
        '''初始化语法树结点。

        `children`参数提供结点的孩子，即与结点关联的其它结点，
        为`setup_stack()`方法使用。
        '''
        self.children = [] if children is None else children
        self.stack = None

    def setup_stack(self, stack):
        self.stack = stack
        for child in self.children:
            child.setup_stack(stack)

    def __str__(self):
        return repr(self)

    def do(self, context=None, local_scope=False):
        '''执行语句，求得程序返回值。

        为保证接口统一，子类覆盖的`do()`方法要实现`context`参数。
        `context`参数接受一个字典，若指定了`local_scope=True`，
        则在调用栈中创建新的变量作用域，其包含的初始变量在`context`中。
        '''
        pass


class FPExpression(FPElement):
    '''表达式。'''

    def __init__(self, spexpr):
        super().__init__()
        self.expr = spexpr
        if isinstance(spexpr, FPExpression):
            self.expr = spexpr.expr

    def __repr__(self):
        return f'FPExpression(\n{indent(sp.pretty(self.expr))}\n)'

    def do(self, context=None, local_scope=False):
        if local_scope:
            self.stack.add_context(context)
        symbols_dict = {
            symbol: self.stack[symbol]
            for symbol in self.expr.atoms(sp.Symbol)}
        functions_dict = {
            function.func: self.stack[function.func]
            for function in self.expr.atoms(sp.Function)}
        result = self.expr.subs(symbols_dict).subs(functions_dict)
        if local_scope:
            self.stack.pop_context()
        return result


class ReturnStatement(FPElement):
    '''返回语句。'''

    def __init__(self, expr):
        self.expr = FPExpression(expr)
        super().__init__([self.expr])

    def __repr__(self):
        return f'Return({self.expr})'

    def do(self, context=None, local_scope=False):
        return self.expr.do()


class Assignment(FPElement):
    '''赋值语句。'''

    def __init__(self, varsymbol, varexpr):
        self.varsymbol, self.varexpr = varsymbol, FPExpression(varexpr)
        super().__init__([self.varexpr])

    def __repr__(self):
        return f'Assignment({self.varsymbol} = {self.varexpr})'

    def do(self, context=None, local_scope=False):
        result = self.varexpr.do()
        self.stack[self.varsymbol] = result
        return result


class FuncDefine(FPElement):
    '''函数定义。'''

    def __init__(self, funcident, funcargs, funcbody):
        self.funcident = sp.Function(str(funcident))          # 函数名称
        self.funcargs = [str(arg) for arg in funcargs]        # 参数列表
        self.funcbody = funcbody if isinstance(
            funcbody, FPElement) else FPExpression(funcbody)  # 函数主体
        super().__init__([self.funcbody])

        @classmethod
        def _func_eval(cls, *args):
            args = list(args)
            kwargs = args.pop() if args and isinstance(
                args[-1], dict | sp.Dict) else {}
            return self.funcbody.do({**{
                sp.Symbol(key): val for key, val in zip(
                    self.funcargs, args)}, **kwargs}, local_scope=True)

        self.function = types.new_class(
            str(funcident), (sp.Function,), {},
            functools.partial(_update_funceval, funceval=_func_eval))

    def __repr__(self):
        return f'FuncDefine({self.funcident}' \
            f'({', '.join(self.funcargs)}) =\n' \
            f'{indent(str(self.funcbody))}\n)'

    def do(self, context=None, local_scope=False):
        self.stack[self.funcident] = self.function


class Judgement(FPElement):
    '''判断语句。'''

    def __init__(self, condition, ifbody, elsebody):
        super().__init__([condition, ifbody] if elsebody is None else [
            condition, ifbody, elsebody])
        self.condition = condition
        self.ifbody, self.elsebody = ifbody, elsebody

    def __repr__(self):
        return f'Judgement(if {self.condition}\n' \
            f'{indent(str(self.ifbody))}\n' \
            f'else\n{indent(str(self.elsebody))}\n)'

    def do(self, context=None, local_scope=False):
        if self.condition.do():
            return self.ifbody.do()
        elif self.elsebody is not None:
            return self.elsebody.do()


class WhileLoop(FPElement):
    '''while循环语句。'''

    def __init__(self, condition, body):
        super().__init__([condition, body])
        self.condition, self.body = condition, body

    def __repr__(self):
        return f'WhileLoop(while {self.condition}\n' \
            f'{indent(str(self.body))}\n)'

    def do(self, context=None, local_scope=False):
        while self.condition.do():
            self.body.do()


class GlobalStatement(FPElement):
    '''global语句。

    将变量暴露于全局作用域，使其可以被程序所有作用域访问和修改。
    '''

    def __init__(self, identifiers):
        super().__init__()
        self.identifiers = identifiers

    def __repr__(self):
        return f'GlobalStatement(\n{indent(str(self.identifiers))}\n)'

    def do(self, context=None, local_scope=False):
        self.stack.add_globals(self.identifiers)


class NonlocalStatement(FPElement):
    '''nonlocal语句。

    将上一层作用域的已知变量暴露于本层作用域，使其可以被本层作用域访问和修改。
    '''

    def __init__(self, identifiers):
        super().__init__()
        self.identifiers = identifiers

    def __repr__(self):
        return f'NonlocalStatement(\n{indent(str(self.identifiers))}\n)'

    def do(self, context=None, local_scope=False):
        self.stack.add_nonlocals(self.identifiers)


class Statements(FPElement):
    '''多条语句组合。'''

    def __init__(self, statements=None):
        super().__init__(statements)
        self.statements = [] if statements is None else statements

    def __repr__(self):
        return f'Statements(\n' \
            + ',\n'.join([indent(str(
                statement)) for statement in self.statements]) + '\n)'

    def do(self, context=None, local_scope=False):
        result = None
        for statement in self.statements:
            result = statement.do()
            if isinstance(statement, ReturnStatement):
                return result
        return result


class StatementsBlock(FPElement):
    '''语句块。'''

    def __init__(self, statements):
        super().__init__([statements])
        self.statements = statements

    def __repr__(self):
        return f'StatementsBlock(\n{indent(str(self.statements))}\n)'

    def do(self, context=None, local_scope=False):
        if local_scope:
            self.stack.add_context(context)
        result = self.statements.do()
        if local_scope:
            self.stack.pop_context()
        return result


def _as_spident(tokens):
    identifier = tokens[0]
    if hasattr(sp, identifier):
        constant = getattr(sp, identifier)
        return sp.Symbol(identifier) if isinstance(
            constant, _function_type | sp.Lambda) else constant
    return sp.Symbol(identifier)


def _as_sprational(tokens):
    return sp.Rational(tokens[0])


def _as_spint(tokens):
    return sp.Integer(tokens[0])


def _process_binops(tokens, specprocs=None, reverse=False):
    result, *tokens = reversed(tokens) if reverse else tokens
    for i in range(0, len(tokens), 2):
        operator, operand = tokens[i], tokens[i + 1]
        result = specprocs[operator](*(
            (operand, result) if reverse else (result, operand)))
    return result


def _process_unops(tokens, specprocs=None):
    *tokens, result = tokens
    for operator in tokens:
        if isinstance(operator, Literal | str):
            result = specprocs[operator](result) \
                if specprocs and operator in specprocs else result
    return result


_as_disjunction = functools.partial(_process_binops, specprocs={'or': sp.Or})
_as_conjunction = functools.partial(
    _process_binops, specprocs={'and': sp.And})
_as_inversion = functools.partial(_process_unops, specprocs={'not': sp.Not})
_as_sum = functools.partial(
    _process_binops, specprocs={'+': operator.add, '-': operator.sub})
_as_term = functools.partial(
    _process_binops, specprocs={'*': operator.mul, '/': operator.truediv})
_as_factor = functools.partial(_process_unops, specprocs={'-': operator.neg})
_as_power = functools.partial(
    _process_binops, specprocs={'^': operator.pow}, reverse=True)
_statements = functools.partial(Statements)


def _as_array(tokens):
    return sp.Array(tokens)


def _as_comparison(tokens):
    prev_operand, *tokens = tokens
    result = []
    for i in range(0, len(tokens), 2):
        operator, operand = tokens[i], tokens[i + 1]
        result.append(COMPDICT[operator](prev_operand, operand))
        prev_operand = operand
    return sp.And(*result) if result else prev_operand


def _as_kwargs(tokens):
    return {
        _ident2symbol(tokens[i]): tokens[i + 2]
        for i in range(0, len(tokens), 3)}


def _as_funcargs(tokens):
    return tokens if isinstance(tokens, list) else [tokens]


def _as_general_parencall(result, *argslist, check_sympyfunc=True):
    flag = True
    for args in argslist:
        result = _as_sympy(result)
        if isinstance(args, FPSliceList):
            result = sp.IndexedBase(result)[args.slices]
            flag = False
            continue
        kwargs = args.pop() if args and isinstance(args[-1], dict) else {}
        str_kwargs = {str(key): val for key, val in kwargs.items()}
        if isinstance(result, _function_type):
            result = result(*args, **str_kwargs)
            flag = False
            continue
        elif check_sympyfunc and flag and hasattr(sp, str(result)):
            function = getattr(sp, str(result))
            if isinstance(function, _function_type):
                result = function(*args, **str_kwargs)
                flag = False
                continue
        if flag:
            # 自定义函数关键字参数直接以字典形式传递
            function = sp.Function(str(result))
            result = function(*args, kwargs) if kwargs else function(*args)
            flag = False
            continue
        raise TypeError(f"'{type(result)}' object is not callable")
    return _as_sympy(result)


def _as_slice(tokens):
    result, temp_token = [], None
    for token in list(tokens) + [',']:
        if token == ',':
            result.append(temp_token)
            temp_token = None
        else:
            temp_token = token
    return FPSliceList(result)


def _as_parencall(tokens):
    return _as_general_parencall(*tokens)


def _as_primary(tokens):
    result, *attributes = tokens
    index = 0
    while index < len(attributes):
        result = _as_sympy(result)
        identifier, argslist = attributes[index + 1], []
        index += 2
        while index < len(attributes) and attributes[index] != DOT:
            argslist.append(attributes[index])
            index += 1
        function = getattr(result, str(identifier))
        if argslist:
            result = _as_general_parencall(
                function, *argslist, check_sympyfunc=False)
        else:
            result = function
    return _as_sympy(result)


def _return_stmt(tokens):
    return ReturnStatement(tokens[1])


def _assignment_stmt(tokens):
    varsymbol, _, varexpr = tokens
    return Assignment(varsymbol, varexpr)


def _funcdefine_stmt(tokens):
    funcident, *funcargs, _, funcbody = tokens
    return FuncDefine(funcident, funcargs, funcbody)


def _judgement(tokens):
    _, condition, ifbody, *elsepart = tokens
    _, elsebody = elsepart if elsepart else (None, None)
    return Judgement(_as_fpelement(condition), ifbody, elsebody)


def _whileloop(tokens):
    _, condition, body = tokens
    return WhileLoop(_as_fpelement(condition), body)


def _globalstmt(tokens):
    _, *identifiers = tokens
    return GlobalStatement(identifiers)


def _nonlocalstmt(tokens):
    _, *identifiers = tokens
    return NonlocalStatement(identifiers)


def _as_statement(tokens):
    return _as_fpelement(tokens[0])


def _as_stmtsblock(tokens):
    return StatementsBlock(tokens[0])


ASSIGN, PLUS, MINUS, TIMES, DIVIDE, POWER, DOT = map(Literal, '=+-*/^.')
LIT_COMMA, COL = map(Literal, ',:')
COMP_LT, COMP_LE, COMP_EQ, COMP_NE, COMP_GE, COMP_GT = map(
    Literal, ['<', '<=', '==', '!=', '>=', '>'])
COMPARISON = COMP_LE | COMP_GE | COMP_NE | COMP_EQ | COMP_LT | COMP_GT
COMPDICT = {
    '<': sp.Lt, '<=': sp.Le, '==': sp.Eq,
    '!=': sp.Ne, '>=': sp.Ge, '>': sp.Gt}
LPAREN, RPAREN, LSQBRK, RSQBRK, LBRACE, RBRACE, SEMICOL, COMMA = map(
    Suppress, '()[]{};,')
KW_NOT, KW_AND, KW_OR, KW_RETURN, KW_IF, KW_ELSE, KW_WHILE = map(
    Literal, ['not', 'and', 'or', 'return', 'if', 'else', 'while'])
KW_GLOBAL, KW_NONLOCAL = map(Literal, ['global', 'nonlocal'])
IDENTIFIER = Word(identchars, identbodychars).set_parse_action(_as_spident)
FLOAT_REGEX = re.compile(
    r'((([1-9]\d*|0)\.\d*)|(([1-9]\d*|0)?\.\d+))([eE][+-]?\d+)?')
INT_REGEX = re.compile(r'[1-9]\d*|0')
FLOAT_ATOM = Regex(FLOAT_REGEX).set_parse_action(_as_sprational)
INT_ATOM = Regex(INT_REGEX).set_parse_action(_as_spint)

'''
BNFs:
<atom>        ::= IDENTIFIER | FLOAT_ATOM | INT_ATOM

<kwargs>      ::= IDENTIFIER "=" <expr> { "," IDENTIFIER "=" <expr> }
<funcargs>    ::= "(" { <expr> "," }
                  [ [ <expr> "," ] <kwargs> | <expr> ] [ "," ] ")"
<slice>       ::= "[" { <expr> "," } <expr> [ "," ] "]"
<parencall>    ::= IDENTIFIER ( <funcargs> | <slice> )+
<array>       ::= "[" [ { ( <array> | <expr> ) "," }
                  ( <array> | <expr> ) [ "," ] ] "]"
<parenexpr>   ::= "(" <expr> ")"
<primary>     ::= ( <array> | <parenexpr> | <parencall> | <atom> )
                  { "." IDENTIFIER { <funcargs> | <slice> } }

<power>       ::= <primary> { "^" <primary> }
<factor>      ::= { "+" | "-" } <power>
<term>        ::= <factor> { "*" <factor> | "/" <factor> }
<sum>         ::= <term> { "+" <term> | "-" <term> }
<comparison>  ::= <sum> { ( "<" | "<=" | "==" | "!=" | ">=" | ">" ) <sum> }
<inversion>   ::= { "not" } <comparison>
<conjunction> ::= <inversion> { "and" <inversion> }
<disjunction> ::= <conjunction> { "or" <conjunction> }
<expr>        ::= <disjunction>

<assignment>  ::= IDENTIFIER "=" <expr>
<funcdefine>  ::= IDENTIFIER LPAREN [ IDENTIFIER { "," IDENTIFIER } [ "," ] ]
                  RPAREN "=" ( <expr> | <stmtsblock> )
<return>      ::= "return" <expr>
<judgement>   ::= "if" <primary> ( <statement> ";" | <stmtsblock> )
                  [ "else" ( <statement> ";" | <stmtsblock> ) ]
<whileloop>   ::= "while" <primary> ( <statement> | <stmtsblock> )
<global>      ::= "global" IDENTIFIER { "," IDENTIFIER } [ "," ]
<nonlocal>    ::= "nonlocal" IDENTIFIER { "," IDENTIFIER } [ "," ]
<statement>   ::= <assignment> | <funcdefine> | <return>
                  | <judgement> | <whileloop> | <global> | <nonlocal>
                  | <stmtsblock> | <expr>
<statements>  ::= <statement> { ";" <statement> } [ ";" ]
<stmtsblock>  ::= "{" <statements> "}"
'''

RULE_atom = IDENTIFIER | FLOAT_ATOM | INT_ATOM
RULE_expr = Forward()
RULE_statement = Forward()
RULE_stmtsblock = Forward()
RULE_array = Forward()

RULE_kwargs = (IDENTIFIER + ASSIGN + RULE_expr + ZeroOrMore(
    COMMA + IDENTIFIER + ASSIGN + RULE_expr)).set_parse_action(_as_kwargs)
RULE_funcargs = (LPAREN + ZeroOrMore(RULE_expr + COMMA) + Opt(
    (Opt(RULE_expr + COMMA) + RULE_kwargs) | RULE_expr) + Opt(
    COMMA) + RPAREN).set_parse_action(_as_funcargs)
RULE_slice = (
    LSQBRK + ZeroOrMore(RULE_expr + LIT_COMMA)
    + RULE_expr + Opt(COMMA) + RSQBRK).set_parse_action(_as_slice)
RULE_parencall = (IDENTIFIER + OneOrMore(
    RULE_funcargs | RULE_slice)).set_parse_action(_as_parencall)
RULE_array << (LSQBRK + Opt(ZeroOrMore(
    (RULE_array | RULE_expr) + COMMA) + (RULE_array | RULE_expr) + Opt(COMMA))
    + RSQBRK).set_parse_action(_as_array)
RULE_parenexpr = LPAREN + RULE_expr + RPAREN
RULE_primary = (
    (RULE_array | RULE_parenexpr | RULE_parencall | RULE_atom)
    + ZeroOrMore(DOT + IDENTIFIER + ZeroOrMore(RULE_funcargs | RULE_slice))
    ).set_parse_action(_as_primary)

RULE_power = (RULE_primary + ZeroOrMore(
    POWER + RULE_primary)).set_parse_action(_as_power)
RULE_factor = (
    ZeroOrMore(PLUS | MINUS) + RULE_power).set_parse_action(_as_factor)
RULE_term = (RULE_factor + ZeroOrMore(
    (TIMES | DIVIDE) + RULE_factor)).set_parse_action(_as_term)
RULE_sum = (RULE_term + ZeroOrMore(
    (PLUS | MINUS) + RULE_term)).set_parse_action(_as_sum)
RULE_comparison = (RULE_sum + ZeroOrMore(
    COMPARISON + RULE_sum)).set_parse_action(_as_comparison)
RULE_inversion = (ZeroOrMore(
    KW_NOT) + RULE_comparison).set_parse_action(_as_inversion)
RULE_conjunction = (RULE_inversion + ZeroOrMore(
    KW_AND + RULE_inversion)).set_parse_action(_as_conjunction)
RULE_disjunction = (RULE_conjunction + ZeroOrMore(
    KW_OR + RULE_conjunction)).set_parse_action(_as_disjunction)
RULE_expr << RULE_disjunction

RULE_assignment = (
    IDENTIFIER + ASSIGN + RULE_expr).set_parse_action(_assignment_stmt)
RULE_funcdefine = (
    IDENTIFIER + LPAREN + Opt(
        IDENTIFIER + ZeroOrMore(COMMA + IDENTIFIER) + Opt(COMMA))
    + RPAREN + ASSIGN + (RULE_expr | RULE_stmtsblock)
    ).set_parse_action(_funcdefine_stmt)
RULE_return = (KW_RETURN + RULE_expr).set_parse_action(_return_stmt)
RULE_judgement = (
    KW_IF + RULE_primary + ((RULE_statement + SEMICOL) | RULE_stmtsblock)
    + Opt(KW_ELSE + ((RULE_statement + SEMICOL) | RULE_stmtsblock))
    ).set_parse_action(_judgement)
RULE_whileloop = (
    KW_WHILE + RULE_primary
    + (RULE_statement | RULE_stmtsblock)).set_parse_action(_whileloop)
RULE_global = (
    KW_GLOBAL + IDENTIFIER + ZeroOrMore(COMMA + IDENTIFIER) + Opt(COMMA)
    ).set_parse_action(_globalstmt)
RULE_nonlocal = (
    KW_NONLOCAL + IDENTIFIER + ZeroOrMore(COMMA + IDENTIFIER) + Opt(COMMA)
    ).set_parse_action(_nonlocalstmt)
RULE_statement << (
    RULE_assignment | RULE_funcdefine | RULE_return
    | RULE_judgement | RULE_whileloop | RULE_global | RULE_nonlocal
    | RULE_stmtsblock | RULE_expr).set_parse_action(_as_statement)

RULE_statements = (
    RULE_statement + ZeroOrMore(SEMICOL + RULE_statement)
    + Opt(SEMICOL)).set_parse_action(_statements)
RULE_stmtsblock << (
    LBRACE + RULE_statements + RBRACE).set_parse_action(_as_stmtsblock)


def fpparse(string):
    '''解析语句为语法树。'''
    parse_result = RULE_statements.parse_string(string, parse_all=True)[0]
    parse_result.setup_stack(ProgramStack())
    return parse_result


def fpeval(parsed_string, context=None):
    '''计算语句的返回值。'''
    if context is not None:
        parsed_string.setup_stack(ProgramStack({
            _ident2symbol(key): val for key, val in context.items()}))
    return sp.simplify(parsed_string.do())
