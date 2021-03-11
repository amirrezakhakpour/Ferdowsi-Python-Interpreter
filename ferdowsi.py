#!/usr/bin/env python3
import sys
import os
from sly import Lexer, Parser

class PPLLexer(Lexer):
	tokens = {
			WRITE, READ, TAKE, RETURN,
			RA, FROM, TO,
			IF, WAS, WASNT, ELSE, THANKS,
			EQUAL,
			NUMBER, STRING, NAME,
			INT_NAME,
			FOR
	}
	ignore = '\t '
	literals = { '=', '+', '-', '*', '/', '(', ')', ',', ';', '.', '،' }
	# Define tokens
	NAME = r'[آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی]+'
	NAME['بنویس'] = WRITE
	NAME['بخوان'] = READ
	NAME['بگیر'] = TAKE
	NAME['برگردان'] = RETURN
	NAME['اگر'] = IF
	NAME['باشد'] = WAS
	NAME['نباشد'] = WASNT
	NAME['برابر'] = EQUAL
	NAME['وگرنه'] = ELSE
	NAME['ممنون'] = THANKS
	NAME['را'] = RA
	NAME['از'] = FROM
	NAME['برای'] = FOR
	NAME['تا'] = TO
	NUMBER = r'((\d+)?\.)?\d+'

	@_(r'«.*?»')
	def STRING(self, t):
		t.value = t.value[1:-1]
		return t

	@_(r'#.*')
	def COMMENT(self, t): pass

	@_(r'\n+')
	def ignore_newline(self, t):
		self.lineno += t.value.count('\n')

class PPLParser(Parser):
	tokens = PPLLexer.tokens

	precedence = (
		('left', '+', '-'),
		('left', '*', '/'),
		('right', 'UMINUS')
	)

	def __init__(self):
		self.env = {}

	@_('')
	def block(self, p): return ('block',)
	@_('statement block')
	def block(self, p): return ('block', p.statement, *p.block[1:])

	@_('expr RA WRITE')
	def statement(self, p):
		return ('out', p.expr)

	@_('NAME RA READ')
	def statement(self, p):
		return ('in', p.NAME)

	@_('NAME RA TAKE')
	def statement(self, p):
		return ('param', p.NAME)

	@_('FOR NAME FROM expr TO expr block THANKS')
	def statement(self, p):
		return ('for_loop', p.NAME, p.expr0, p.expr1, p.block)

	@_('IF condition block ELSE block THANKS')
	def statement(self, p):
		return ('if', p.condition, p.block0, p.block1)
	@_('IF condition block THANKS')
	def statement(self, p):
		return ('if', p.condition, p.block)

	@_('expr EQUAL expr')
	def condition(self, p):
		return ('equals', p.expr0, p.expr1)

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
		return ('sub', ('num', '0'), p.expr)

	@_('NAME')
	def expr(self, p):
		return ('var', p.NAME)
	@_('NUMBER')
	def expr(self, p):
		return ('num', p.NUMBER)
	@_('STRING')
	def expr(self, p):
		return ('str', p.STRING)

class PPLExecute(object):
	def __init__(self, tree, env):
		self.env = env
		result = self.walk(tree)
		if result is not None: print(result)

	def walk(self, node):
		if node[0] == 'block':
			for stmt in node[1:]: self.walk(stmt)
		if node[0] == 'num':
			return float(node[1])
		if node[0] == 'str':
			return node[1]
		if node[0] == 'out':
			print(self.walk(node[1]))
		if node[0] == 'in':
			self.env[node[1]] = input()
		if node[0] == 'if':
			result = self.walk(node[1])
			if result: return self.walk(node[2])
			if node[3]: return self.walk(node[3])
		if node[0] == 'equals':
			return self.walk(node[1]) == self.walk(node[2])
		elif node[0] == 'add':
			return self.walk(node[1]) + self.walk(node[2])
		elif node[0] == 'sub':
			return self.walk(node[1]) - self.walk(node[2])
		elif node[0] == 'mul':
			return self.walk(node[1]) * self.walk(node[2])
		elif node[0] == 'div':
			return self.walk(node[1]) / self.walk(node[2])
		if node[0] == 'var':
			if node[1] in self.env:
				return self.env[node[1]]
			else:
				raise Exception('undefined variable')

if __name__ == '__main__':
	lexer = PPLLexer()
	parser = PPLParser()
	env = {}
	if len(sys.argv) < 2: print("باید آدرس فایل را هنگام اجرای برنامه مشخص کنید")
	elif not os.path.exists(sys.argv[1]): print("فایل ورودی وجود ندارد")
	elif os.path.isdir(sys.argv[1]): print("این یک پوشه هست و نه فایل")
	else:
		with open(sys.argv[1], encoding="utf-8") as fp:
			tokens = lexer.tokenize(fp.read())
			tree = parser.parse(tokens)
			print(tree)
			PPLExecute(tree, env)
