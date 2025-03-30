#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.tokens import Token
from core.errors import PinLangSyntaxError
from core import debug_print

class Lexer:
    """词法分析器"""
    def __init__(self, text, file_name=None):
        self.text = text
        self.file_name = file_name
        self.pos = 0
        self.current_char = self.text[0] if self.text else None
        self.line_num = 1
        
        # 关键字映射
        self.keywords = {
            'dayin': 'PRINT',
            'dy': 'PRINT_SHORT',
            'bianliang': 'VAR_DEFINE',
            'bl': 'VAR_DEFINE_SHORT',
            'liebiao': 'LIST',
            'chuangjian': 'CREATE',
            'huoqu': 'GET',
            'bianji': 'EDIT',  # 新增编辑关键字
            'bianhao': 'INDEX',
            'chuandi': 'PASS',
            'jisuan': 'CALCULATE',
            'zhuanhuan': 'CONVERT',
            'shuzi': 'NUMBER_TYPE',
            'zifu': 'STRING_TYPE',
            'panduan': 'IF',
            'fouze': 'ELSE',
            'shuru': 'INPUT',
            'jin': 'RESTRICT',
            'tiao': 'JUMP',
            'ciwenjian': 'CURRENT_FILE',
            'hang': 'LINE',
            'xunhuan': 'LOOP',    # 新增循环关键字
            'cishu': 'LOOP_COUNT' # 循环次数关键字
        }

    def error(self, message):
        """报告词法错误"""
        raise PinLangSyntaxError(message, self.line_num, self.file_name)

    def advance(self):
        """向前移动一个字符"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            
    def skip_whitespace(self):
        """跳过空白字符"""
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line_num += 1
            self.advance()
            
    def skip_comment(self):
        """跳过注释"""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
            
    def string(self):
        """处理字符串字面量"""
        result = ''
        # 跳过开始的引号（单引号或双引号）
        quote_char = self.current_char
        self.advance()
        
        while self.current_char is not None and self.current_char != quote_char:
            if self.current_char == '\n':
                self.error("字符串未闭合")
            result += self.current_char
            self.advance()
            
        # 跳过结束的引号
        if self.current_char == quote_char:
            self.advance()
        else:
            self.error("字符串未闭合")
            
        return result
        
    def identifier(self):
        """处理标识符或关键字"""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char in ('_')):
            result += self.current_char
            self.advance()
            
        token_type = self.keywords.get(result, 'ID')
        return Token(token_type, result, self.line_num)
        
    def number(self):
        """处理数字"""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
            
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
                
            return Token('FLOAT', float(result), self.line_num)
        
        return Token('INTEGER', int(result), self.line_num)
        
    def get_next_token(self):
        """词法分析主函数，返回下一个标记"""
        while self.current_char is not None:
            # 处理空白字符
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # 处理注释
            if self.current_char == '#':
                self.skip_comment()
                continue
                
            # 处理标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
                
            # 处理数字
            if self.current_char.isdigit():
                return self.number()
                
            # 处理字符串
            if self.current_char in ('"', "'"):
                return Token('STRING', self.string(), self.line_num)
                
            # 处理特殊字符和操作符
            if self.current_char == '=':
                self.advance()
                if self.current_char == '!':  # 检查是否是不等号 =!
                    self.advance()
                    return Token('NOT_EQUALS', '=!', self.line_num)
                return Token('EQUALS', '=', self.line_num)
                
            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+', self.line_num)
                
            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-', self.line_num)
                
            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY', '*', self.line_num)
                
            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/', self.line_num)
                
            if self.current_char == '(' or self.current_char == '（':
                self.advance()
                return Token('LPAREN', '(', self.line_num)
                
            if self.current_char == ')' or self.current_char == '）':
                self.advance()
                return Token('RPAREN', ')', self.line_num)
                
            if self.current_char == '[':
                self.advance()
                return Token('LBRACKET', '[', self.line_num)
                
            if self.current_char == ']':
                self.advance()
                return Token('RBRACKET', ']', self.line_num)
                
            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',', self.line_num)
                
            if self.current_char == ':':
                self.advance()
                return Token('COLON', ':', self.line_num)
                
            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':  # 检查是否是大于等于 >=
                    self.advance()
                    return Token('GE', '>=', self.line_num)
                return Token('GT', '>', self.line_num)
                
            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':  # 检查是否是小于等于 <=
                    self.advance()
                    return Token('LE', '<=', self.line_num)
                return Token('LT', '<', self.line_num)
                
            self.error(f"无法识别的字符: '{self.current_char}'")
            
        return Token('EOF', None, self.line_num)

    def tokenize(self):
        """将整个输入文本转换为标记列表"""
        tokens = []
        token = self.get_next_token()
        while token.type != 'EOF':
            tokens.append(token)
            token = self.get_next_token()
        tokens.append(token)  # 添加EOF标记
        return tokens 