#!/usr/bin/python

""" MapCSS lexer """

import re
import ply.lex as lex
from mapcss_parser import error

# Compute column.
#     input is the input text string
#     token is a token instance
# Basically taken from the PLY documentation
def find_column(input,token):
    last_cr = input.rfind('\n',0,token.lexpos)
    return (token.lexpos - last_cr)

states = (
    ('condition', 'exclusive'),
    ('regex', 'exclusive'),
    ('actionkey', 'exclusive'),
    ('actionvalue', 'exclusive'),
    ('tagvalue', 'exclusive'),
    ('import', 'exclusive'),
    ('eval', 'exclusive'),
)

tokens = (
    #Comments in C-style
    'COMMENT',
    #Comments in C++-style
    'CXXCOMMENT',

    #Rule sublect
    'SUBJECT',
    'SUBPART',
    'CLASS',
    'ZOOM',
    'MEMBEROF',

    #Conditions
    'LSQBRACE',
    'RSQBRACE',
    'SIGN',
    'NOT',
    'IDENTIFIER',
    'REGEX_START',

    #Regex
    'REGEX_BODY',

    #Actions
    'LCBRACE',
    'RCBRACE',
    'KEY',
    'VALUE',
    'COLON',
    'SEMICOLON',
    'COMMA',
    'EXIT',
    'EQUALS',

    #Import
    'IMPORT',
    'URL',
    'PSEUDOCLASS',

    #eval
    'EVAL',
    'LPAREN',
    'RPAREN',
    'STRING',
    'NUMBER',
    'OPERATION',
    'FUNCTION',
)

# Completely ignored characters
t_ANY_ignore  = ' \t'

t_SUBJECT = r'\w+|\*'
t_condition_SIGN = r'=~|<>|<=|>=|!=|<|>|=|~='
t_condition_NOT = r'\!'
t_condition_IDENTIFIER = r'[^/!<>=\[\]~]+'
t_COMMA = r','
t_actionkey_KEY = r'[\w-]+'
t_actionkey_CLASS = r'\.\w+'
t_CLASS = r'\.\w+'
t_PSEUDOCLASS = r':\w+'
t_import_PSEUDOCLASS = r'\w+'

t_eval_NUMBER = r'\d+(\.\d+)?'
t_eval_OPERATION = r'\+|-|\*|\/|==|<>|!=|<=|>=|>|<|eq|ne|\.'
t_eval_FUNCTION = r'\w+'
t_eval_COMMA = r','

def t_ANY_CXXCOMMENT(t):
    r'//[^\n]*'
    pass

def t_MEMBEROF(t):
    r'>'
    return t

def t_SUBPART(t):
    r'::(:?[\w\d-]+|\*)'
    t.value = t.value[2:]
    return t

def t_eval_LPAREN(t):
    r'\('
    t.lexer.level += 1
    return t

def t_eval_RPAREN(t):
    r'\)'
    t.lexer.level -= 1
    if t.lexer.level == 0:
        t.lexer.pop_state()
    return t

def t_eval_STRING(t):
    r'"[^"\\]*(:?\\.[^"\\]*)*"'
    t.value = t.value[1:-1]
    return t

def t_tagvalue_EVAL(t):
    r'eval'
    t.lexer.push_state('eval')
    t.lexer.level = 0
    return t

def t_actionvalue_EVAL(t):
    r'eval'
    t.lexer.push_state('eval')
    t.lexer.level = 0
    return t

def t_actionvalue_VALUE(t):
    r'((?P<quote>["\'])[^"\\]*(:?\\.[^"\\]*)*(?P=quote))|([#:\w\-\.,\\\/ ]+)'
    t.value = t.value.strip(r'"\'')
    return t

def t_tagvalue_VALUE(t):
    r'((?P<quote>["\'])[^"\\]*(:?\\.[^"\\]*)*(?P=quote))|([#:\w\-\.,\\\/]+)'
    t.value = t.value.strip(r'"\'')
    return t

def t_import_SEMICOLON(t):
    r';'
    t.lexer.pop_state()
    return t

def t_IMPORT(t):
    r'@import'
    t.lexer.push_state('import')
    return t

def t_import_URL(t):
    r'url\((?P<quote>["\'])([\w\-\.\\/]+)(?P=quote)\)'
    t.value = t.value[5:-2]
    return t

def t_ANY_COMMENT(t):
    r'/\*.*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_ZOOM(t):
    r'\|(z|s)\d*(\-\d*)?'
    return t

def t_actionkey_COLON(t):
    r':'
    t.lexer.pop_state()
    t.lexer.push_state('actionvalue')
    return t

def t_actionkey_SEMICOLON(t):
    r';'
    t.lexer.pop_state()
    t.lexer.push_state('actionkey')
    pass

def t_actionkey_EQUALS(t):
    r'='
    t.lexer.push_state('tagvalue')
    return t

def t_actionkey_EXIT(t):
    r'exit';
    t.lexer.pop_state()
    t.lexer.push_state('actionvalue')
    return t

def t_actionkey_RCBRACE(t):
    r'}'
    t.lexer.pop_state()
    return t

def t_actionvalue_SEMICOLON(t):
    r';'
    t.lexer.pop_state()
    t.lexer.push_state('actionkey')
    pass

def t_actionvalue_RCBRACE(t):
    r'}'
    t.lexer.pop_state()
    return t

def t_tagvalue_SEMICOLON(t):
    r';'
    t.lexer.begin('actionkey')
    pass

def t_LCBRACE(t):
    r'{'
    t.lexer.push_state('actionkey')
    return t

def t_LSQBRACE(t):
    r'\['
    t.lexer.push_state('condition')
    return t

def t_condition_REGEX_START(t):
    r'/'
    t.lexer.push_state('regex')
    return t

def t_regex_REGEX_BODY(t):
    r'[^/]*/'
    t.lexer.pop_state()
    return t

def t_condition_RSQBRACE(t):
    r'\]'
    t.lexer.pop_state()
    return t

# Error handling rule
def t_ANY_error(t):
    raise error.MapCSSError("Illegal character '%s' at line %i position %i" % (t.value[0], t.lexer.lineno, find_column(t.lexer.lexdata, t)))

# Define a rule so we can track line numbers
def t_ANY_newline(t):
    r'\r?\n'
    t.lexer.lineno += 1

lexer = lex.lex(reflags=re.DOTALL)

if __name__ == '__main__':
    lex.runmain()
