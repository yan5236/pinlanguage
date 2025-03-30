#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.tokens import Token
from core.errors import PinLangSyntaxError
from core.ast import *
from core import debug_print

class Parser:
    """语法分析器"""
    def __init__(self, lexer, tokens=None):
        self.lexer = lexer
        self.tokens = tokens if tokens is not None else lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def error(self, message):
        """报告语法错误"""
        token = self.current_token
        raise PinLangSyntaxError(message, token.line_num, self.lexer.file_name)

    def eat(self, token_type):
        """消费一个标记"""
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = Token('EOF', None, -1)
        else:
            self.error(f"期望 {token_type}，但得到 {self.current_token.type}")

    def parse(self):
        """解析入口点"""
        try:
            debug_print("开始解析程序...")
            result = self.parse_program()
            debug_print(f"解析完成，生成了 {len(result)} 个语句节点")
            return result
        except KeyboardInterrupt:
            debug_print("\n解析被用户中断")
            return []  # 返回空语句列表
        except Exception as e:
            debug_print(f"解析过程中出现未捕获的异常: {str(e)}")
            if hasattr(debug_print, '__self__') and debug_print.__self__.DEBUG_MODE:
                import traceback
                traceback.print_exc()
            raise

    def parse_program(self):
        """解析完整程序，返回语句列表"""
        statements = []
        
        debug_print("开始解析程序...")
        try:
            while self.current_token.type != 'EOF':
                debug_print(f"当前解析位置: {self.pos}, 当前token: {self.current_token}")
                
                # 检查是否是标记行（形如 hang_5）
                if self.current_token.type == 'ID' and self.current_token.value.startswith('hang_'):
                    label_name = self.current_token.value
                    line_num = self.current_token.line_num
                    debug_print(f"发现标记点: {label_name}")
                    statements.append(LabelNode(label_name, line_num))
                    self.pos += 1
                    if self.pos < len(self.tokens):
                        self.current_token = self.tokens[self.pos]
                    continue
                
                # 解析常规语句
                if self.current_token.type in ('PRINT', 'PRINT_SHORT', 'VAR_DEFINE', 'VAR_DEFINE_SHORT', 
                                             'LIST', 'CALCULATE', 'CONVERT', 'IF', 'INPUT', 'JUMP', 'LOOP'):
                    try:
                        stmt = self.statement()
                        debug_print(f"成功解析语句: {stmt.__class__.__name__}")
                        statements.append(stmt)
                    except PinLangSyntaxError as e:
                        # 语法错误时，尝试恢复并继续解析
                        print(e)
                        debug_print(f"解析语句出错: {str(e)}")
                        # 尝试跳到下一条语句
                        while (self.pos < len(self.tokens) and 
                               self.current_token.type not in ('PRINT', 'PRINT_SHORT', 'VAR_DEFINE', 'VAR_DEFINE_SHORT', 
                                                             'LIST', 'CALCULATE', 'CONVERT', 'IF', 'INPUT', 'JUMP', 'LOOP')):
                            self.pos += 1
                            if self.pos < len(self.tokens):
                                self.current_token = self.tokens[self.pos]
                else:
                    # 如果不是语句开始，跳过
                    debug_print(f"跳过非语句开始token: {self.current_token}")
                    self.pos += 1
                    if self.pos < len(self.tokens):
                        self.current_token = self.tokens[self.pos]
        except KeyboardInterrupt:
            debug_print("\n解析被中断")
            return statements
            
        debug_print(f"解析完成，共 {len(statements)} 个语句")
        return statements

    def statement(self):
        """解析语句"""
        token = self.current_token
        debug_print(f"解析语句，当前token: {token}")
        
        try:
            if token.type in ('PRINT', 'PRINT_SHORT'):
                return self.print_statement()
            elif token.type in ('VAR_DEFINE', 'VAR_DEFINE_SHORT'):
                return self.var_define_statement()
            elif token.type == 'LIST':
                next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
                debug_print(f"  列表操作，下一个token: {next_token}")
                if next_token and next_token.type == 'CREATE':
                    return self.list_create_statement()
                elif next_token and next_token.type == 'GET':
                    return self.list_get_statement()
                elif next_token and next_token.type == 'EDIT':
                    return self.list_edit_statement()
                else:
                    self.error("列表操作后应该是 'chuangjian', 'huoqu' 或 'bianji'")
            elif token.type == 'CALCULATE':
                debug_print(f"  准备解析计算语句，当前token: {token}")
                return self.calculate_statement()
            elif token.type == 'CONVERT':
                return self.convert_statement()
            elif token.type == 'IF':
                return self.if_statement()
            elif token.type == 'INPUT':
                return self.input_statement()
            elif token.type == 'JUMP':
                return self.jump_statement()
            elif token.type == 'LOOP':
                return self.loop_statement()
            elif token.type == 'ELSE':
                # 在这里处理'fouze'关键字，通常在if语句中处理，
                # 但为了防止它单独出现导致错误，这里返回None
                self.eat('ELSE')
                if self.current_token.type == 'COLON':
                    self.eat('COLON')
                return None
            else:
                self.error(f"未知的语句类型: {token.type}")
        except Exception as e:
            debug_print(f"  解析语句出错: {str(e)}")
            raise

    def print_statement(self):
        """解析打印语句"""
        token = self.current_token
        line_num = token.line_num
        self.eat(token.type)  # 消费 PRINT 或 PRINT_SHORT
        
        # 检查是否有左括号（英文或中文）
        if self.current_token.type == 'LPAREN':
            self.eat('LPAREN')
            
            # 解析打印内容
            if self.current_token.type == 'STRING':
                value = LiteralNode(self.current_token.value, line_num)
                self.eat('STRING')
            elif self.current_token.type == 'ID':
                value = VarNode(self.current_token.value, line_num)
                self.eat('ID')
            elif self.current_token.type in ('INTEGER', 'FLOAT'):
                value = LiteralNode(self.current_token.value, line_num)
                self.eat(self.current_token.type)
            else:
                value = self.expr()
            
            # 检查是否有右括号（英文或中文）
            if self.current_token.type == 'RPAREN':
                self.eat('RPAREN')
            else:
                self.error(f"打印语句需要右括号，但得到 {self.current_token.type}")
        else:
            self.error(f"打印语句需要左括号，但得到 {self.current_token.type}")
        
        return PrintNode(value, line_num)

    def var_define_statement(self):
        """解析变量定义语句"""
        token = self.current_token
        line_num = token.line_num
        self.eat(token.type)  # 消费 VAR_DEFINE 或 VAR_DEFINE_SHORT
        
        var_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        
        if self.current_token.type == 'STRING':
            value = LiteralNode(self.current_token.value, line_num)
            self.eat('STRING')
        elif self.current_token.type in ('INTEGER', 'FLOAT'):
            value = LiteralNode(self.current_token.value, line_num)
            self.eat(self.current_token.type)
        else:
            value = self.expr()
            
        return VarDeclNode(var_name, value, line_num)

    def list_create_statement(self):
        """解析列表创建语句"""
        line_num = self.current_token.line_num
        self.eat('LIST')
        self.eat('CREATE')
        
        list_name = self.current_token.value
        self.eat('ID')
        self.eat('EQUALS')
        
        self.eat('LBRACKET')
        values = []
        
        # 处理空列表的情况
        if self.current_token.type == 'RBRACKET':
            self.eat('RBRACKET')
            return ListCreateNode(list_name, values, line_num)
            
        # 处理非空列表
        if self.current_token.type == 'STRING':
            values.append(LiteralNode(self.current_token.value, line_num))
            self.eat('STRING')
        elif self.current_token.type in ('INTEGER', 'FLOAT'):
            values.append(LiteralNode(self.current_token.value, line_num))
            self.eat(self.current_token.type)
        else:
            values.append(self.expr())
            
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            if self.current_token.type == 'STRING':
                values.append(LiteralNode(self.current_token.value, line_num))
                self.eat('STRING')
            elif self.current_token.type in ('INTEGER', 'FLOAT'):
                values.append(LiteralNode(self.current_token.value, line_num))
                self.eat(self.current_token.type)
            else:
                values.append(self.expr())
                
        self.eat('RBRACKET')
        return ListCreateNode(list_name, values, line_num)

    def list_get_statement(self):
        """解析列表获取语句"""
        line_num = self.current_token.line_num
        self.eat('LIST')
        self.eat('GET')
        
        list_name = self.current_token.value
        self.eat('ID')
        
        self.eat('INDEX')
        self.eat('EQUALS')
        
        if self.current_token.type == 'INTEGER':
            index = self.current_token.value
            self.eat('INTEGER')
        else:
            index = self.expr()
            
        self.eat('PASS')
        self.eat('VAR_DEFINE')
        self.eat('EQUALS')
        
        target_var = self.current_token.value
        self.eat('ID')
        
        return ListGetNode(list_name, index, target_var, line_num)

    def list_edit_statement(self):
        """解析列表编辑语句"""
        line_num = self.current_token.line_num
        self.eat('LIST')
        self.eat('EDIT')
        
        list_name = self.current_token.value
        self.eat('ID')
        
        self.eat('INDEX')
        self.eat('EQUALS')
        
        if self.current_token.type == 'INTEGER':
            index = self.current_token.value
            self.eat('INTEGER')
        else:
            index = self.expr()
            
        self.eat('PASS')
        
        # 处理传入的值，可以是字符串函数如 zifu("VIVO") 或其他表达式
        if self.current_token.type == 'STRING_TYPE':
            self.eat('STRING_TYPE')
            self.eat('LPAREN')
            value = self.current_token.value
            self.eat('STRING')
            self.eat('RPAREN')
            value = LiteralNode(value, line_num)
        elif self.current_token.type == 'NUMBER_TYPE':
            self.eat('NUMBER_TYPE')
            self.eat('LPAREN')
            if self.current_token.type in ('INTEGER', 'FLOAT'):
                value = LiteralNode(self.current_token.value, line_num)
                self.eat(self.current_token.type)
            else:
                value = self.expr()
            self.eat('RPAREN')
        else:
            value = self.expr()
            
        return ListEditNode(list_name, index, value, line_num)

    def calculate_statement(self):
        """解析计算语句"""
        debug_print(f"开始解析计算语句，当前token: {self.current_token}")
        line_num = self.current_token.line_num
        self.eat('CALCULATE')
        
        # 保存当前位置，用于计算表达式的结束位置
        start_pos = self.pos
        
        # 找到等号的位置
        equals_pos = None
        for i in range(start_pos, len(self.tokens)):
            if self.tokens[i].type == 'EQUALS':
                equals_pos = i
                break
        
        if equals_pos is None:
            self.error("计算语句需要等号")
        
        # 临时保存当前位置
        temp_pos = self.pos
        temp_token = self.current_token
        
        # 构建表达式
        expr_end = equals_pos - 1
        expr_tokens = self.tokens[start_pos:expr_end+1]
        debug_print(f"  表达式tokens: {[str(t) for t in expr_tokens]}")
        
        # 解析表达式
        expr = None
        if len(expr_tokens) == 1 and expr_tokens[0].type in ('INTEGER', 'FLOAT'):
            # 简单数字
            expr = LiteralNode(expr_tokens[0].value, expr_tokens[0].line_num)
        elif len(expr_tokens) == 1 and expr_tokens[0].type == 'ID':
            # 简单变量
            expr = VarNode(expr_tokens[0].value, expr_tokens[0].line_num)
        elif len(expr_tokens) == 3 and expr_tokens[1].type in ('PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE'):
            # 简单二元操作
            left = LiteralNode(expr_tokens[0].value, expr_tokens[0].line_num) if expr_tokens[0].type in ('INTEGER', 'FLOAT') else VarNode(expr_tokens[0].value, expr_tokens[0].line_num)
            op = expr_tokens[1].value
            right = LiteralNode(expr_tokens[2].value, expr_tokens[2].line_num) if expr_tokens[2].type in ('INTEGER', 'FLOAT') else VarNode(expr_tokens[2].value, expr_tokens[2].line_num)
            expr = BinOpNode(left, op, right, expr_tokens[0].line_num)
        else:
            # 未处理的复杂表达式
            self.error("暂不支持复杂的计算表达式")
        
        # 恢复并前进到等号位置
        self.pos = equals_pos
        self.current_token = self.tokens[self.pos]
        
        # 处理等号和目标变量
        debug_print(f"  处理等号，当前token: {self.current_token}")
        self.eat('EQUALS')
        
        debug_print(f"  处理目标变量，当前token: {self.current_token}")
        if self.current_token.type == 'ID':
            target_var = self.current_token.value
            self.eat('ID')
        else:
            self.error(f"计算语句的结果需要赋值给变量，但得到 {self.current_token.type}")
        
        debug_print(f"  计算语句解析完成")
        return CalculateNode(expr, target_var, line_num)

    def convert_statement(self):
        """解析类型转换语句"""
        line_num = self.current_token.line_num
        self.eat('CONVERT')
        
        value_name = self.current_token.value
        self.eat('ID')
        
        type_name = self.current_token.value
        if self.current_token.type in ('NUMBER_TYPE', 'STRING_TYPE'):
            self.eat(self.current_token.type)
        else:
            self.error(f"无效的类型名: {self.current_token.value}")
        
        self.eat('EQUALS')
        
        target_var = self.current_token.value
        self.eat('ID')
        
        return ConvertNode(value_name, type_name, target_var, line_num)

    def if_statement(self):
        """解析条件语句"""
        debug_print(f"执行条件判断，条件: {self.current_token.type}")
        line_num = self.current_token.line_num
        self.eat('IF')
        
        debug_print("解析条件表达式...")
        condition = self.expr()
        debug_print(f"条件表达式解析完成: {condition.__class__.__name__}")
        
        self.eat('COLON')
        debug_print("开始解析if主体...")
        
        # 解析if主体（缩进的代码块）
        body = []
        while self.pos < len(self.tokens) and self.current_token.type != 'ELSE' and self.current_token.type != 'EOF':
            if self.current_token.type in ('PRINT', 'PRINT_SHORT', 'VAR_DEFINE', 'VAR_DEFINE_SHORT', 
                                          'LIST', 'CALCULATE', 'CONVERT', 'IF', 'INPUT', 'JUMP', 'LOOP'):
                stmt = self.statement()
                debug_print(f"  解析到if主体语句: {stmt.__class__.__name__}")
                body.append(stmt)
            else:
                # 如果不是有效的语句开始，跳过
                debug_print(f"  跳过非语句开始token: {self.current_token}")
                self.pos += 1
                if self.pos < len(self.tokens):
                    self.current_token = self.tokens[self.pos]
                else:
                    break
        
        debug_print(f"if主体解析完成，共 {len(body)} 个语句")
        
        # 解析else块（如果有）
        else_body = []
        if self.current_token.type == 'ELSE':
            debug_print("解析else部分...")
            self.eat('ELSE')
            if self.current_token.type == 'COLON':
                self.eat('COLON')
                
            debug_print("开始解析else主体...")
            while self.pos < len(self.tokens) and self.current_token.type != 'EOF':
                if self.current_token.type in ('PRINT', 'PRINT_SHORT', 'VAR_DEFINE', 'VAR_DEFINE_SHORT', 
                                              'LIST', 'CALCULATE', 'CONVERT', 'IF', 'INPUT', 'JUMP', 'LOOP'):
                    stmt = self.statement()
                    debug_print(f"  解析到else主体语句: {stmt.__class__.__name__}")
                    else_body.append(stmt)
                else:
                    # 如果不是有效的语句开始，跳过
                    debug_print(f"  跳过非语句开始token: {self.current_token}")
                    self.pos += 1
                    if self.pos < len(self.tokens):
                        self.current_token = self.tokens[self.pos]
                    else:
                        break
            
            debug_print(f"else主体解析完成，共 {len(else_body)} 个语句")
        
        debug_print("if语句解析完成")
        return IfNode(condition, body, else_body, line_num)

    def input_statement(self):
        """解析输入语句"""
        line_num = self.current_token.line_num
        self.eat('INPUT')
        
        self.eat('LPAREN')
        prompt = self.current_token.value
        self.eat('STRING')
        self.eat('RPAREN')
        
        self.eat('EQUALS')
        
        target_var = self.current_token.value
        self.eat('ID')
        
        # 处理可选的限制
        restriction = None
        if self.current_token.type == 'RESTRICT':
            self.eat('RESTRICT')
            self.eat('LPAREN')
            restriction = self.current_token.value
            self.eat('STRING_TYPE')  # 例如 'zifu'
            self.eat('RPAREN')
            
        return InputNode(prompt, target_var, restriction, line_num)

    def jump_statement(self):
        """解析跳转语句"""
        debug_print(f"开始解析跳转语句, 当前位置: {self.pos}, 当前token: {self.current_token}")
        line_num = self.current_token.line_num
        self.eat('JUMP')
        
        # 处理文件名
        file_name = None
        if self.current_token.type == 'CURRENT_FILE':
            debug_print("  跳转到当前文件")
            file_name = 'current'
            self.eat('CURRENT_FILE')
        else:
            file_name = self.current_token.value
            debug_print(f"  跳转到文件: {file_name}")
            self.eat('ID')
            
        # 处理目标类型
        target_type = None
        target_value = None
        
        if self.current_token.type == 'LINE':
            target_type = 'hang'
            debug_print("  跳转到指定行")
            self.eat('LINE')
        elif self.current_token.type == 'INPUT':
            target_type = 'shuru'
            debug_print("  跳转到输入语句")
            self.eat('INPUT')
        else:
            target_type = self.current_token.value
            debug_print(f"  跳转到自定义目标: {target_type}")
            self.eat('ID')  # 例如可能是其他类型的标记
            
        # 处理目标值
        self.eat('EQUALS')
        
        target_value = self.current_token.value
        debug_print(f"  跳转目标索引: {target_value}")
        self.eat('INTEGER')
        
        debug_print(f"跳转语句解析完成: {file_name}, {target_type}, {target_value}")
        return JumpNode(file_name, target_type, target_value, line_num)

    def loop_statement(self):
        """解析循环语句"""
        debug_print(f"执行循环语句，当前token: {self.current_token}")
        line_num = self.current_token.line_num
        self.eat('LOOP')
        
        # 解析循环变量和条件（如果有）
        variable = None
        condition = None
        value = None
        
        # 检查是否存在变量和条件
        if self.current_token.type == 'ID':
            debug_print(f"  循环变量: {self.current_token.value}")
            variable = self.current_token.value
            self.eat('ID')
            
            # 检查是否有条件（=, =!, >, <, >=, <=）
            if self.current_token.type in ('EQUALS', 'NOT_EQUALS', 'GT', 'LT', 'GE', 'LE'):
                debug_print(f"  循环条件: {self.current_token.value}")
                condition = self.current_token.value
                self.eat(self.current_token.type)
                
                # 获取条件值
                if self.current_token.type in ('INTEGER', 'FLOAT'):
                    debug_print(f"  条件值: {self.current_token.value}")
                    value = self.current_token.value
                    self.eat(self.current_token.type)
                elif self.current_token.type == 'ID':
                    debug_print(f"  条件值变量: {self.current_token.value}")
                    value = VarNode(self.current_token.value, self.current_token.line_num)
                    self.eat('ID')
                else:
                    self.error(f"循环条件后需要数字或变量，但得到了 {self.current_token.type}")
        
        # 解析循环次数
        count = None
        if self.current_token.type == 'LOOP_COUNT':
            debug_print("  解析循环次数")
            self.eat('LOOP_COUNT')
            self.eat('EQUALS')
            
            if self.current_token.type in ('INTEGER', 'FLOAT'):
                count = self.current_token.value
                debug_print(f"  循环次数: {count}")
                self.eat(self.current_token.type)
            elif self.current_token.type == 'ID':
                count = VarNode(self.current_token.value, self.current_token.line_num)
                debug_print(f"  循环次数变量: {self.current_token.value}")
                self.eat('ID')
            else:
                self.error(f"循环次数后需要数字或变量，但得到了 {self.current_token.type}")
        
        # 解析循环主体
        debug_print("  解析循环主体")
        self.eat('COLON')
        
        # 解析循环体语句
        body = []
        while self.pos < len(self.tokens) and self.current_token.type != 'EOF':
            # 检查是否达到循环体的末尾（通常是通过缩进来判断，但这里简化处理）
            if self.current_token.type in ('PRINT', 'PRINT_SHORT', 'VAR_DEFINE', 'VAR_DEFINE_SHORT', 
                                         'LIST', 'CALCULATE', 'CONVERT', 'IF', 'INPUT', 'JUMP', 'LOOP'):
                # 检查是否在下一个顶级语句开始处
                if len(body) > 0 and self.current_token.line_num > body[-1].line_num + 1:
                    # 如果有一行或多行间隔，可能表示循环体结束
                    # 这是一个简化的逻辑，实际中可能需要更复杂的处理
                    break
                
                stmt = self.statement()
                debug_print(f"  解析到循环体语句: {stmt.__class__.__name__}")
                body.append(stmt)
            else:
                # 如果不是有效的语句开始，跳过
                debug_print(f"  跳过非语句开始token: {self.current_token}")
                self.pos += 1
                if self.pos < len(self.tokens):
                    self.current_token = self.tokens[self.pos]
                else:
                    break
        
        debug_print(f"循环解析完成，共 {len(body)} 个语句")
        return LoopNode(variable, condition, value, count, body, line_num)

    def expr(self):
        """解析表达式"""
        try:
            debug_print(f"  开始解析表达式，位置: {self.pos}, 当前token: {self.current_token}")
            result = self.comparison()
            debug_print(f"  表达式解析结果: {result.__class__.__name__}, 位置: {self.pos}, 当前token: {self.current_token}")
            return result
        except Exception as e:
            debug_print(f"  表达式解析出错: {str(e)}")
            raise

    def comparison(self):
        """解析比较表达式"""
        try:
            debug_print(f"    开始解析比较表达式，位置: {self.pos}, 当前token: {self.current_token}")
            node = self.add()
            
            while self.current_token.type in ('GT', 'LT', 'GE', 'LE', 'EQUALS', 'NOT_EQUALS'):
                token = self.current_token
                debug_print(f"    比较运算符: {token.value}, 类型: {token.type}")
                self.eat(token.type)
                right_node = self.add()
                debug_print(f"    比较右侧: {right_node.__class__.__name__}")
                node = BinOpNode(node, token.value, right_node, token.line_num)
                
            debug_print(f"    比较表达式解析结果: {node.__class__.__name__}")
            return node
        except Exception as e:
            debug_print(f"    比较表达式解析出错: {str(e)}")
            raise

    def add(self):
        """解析加减表达式"""
        debug_print(f"      开始解析加减表达式，位置: {self.pos}, 当前token: {self.current_token}")
        node = self.term()
        
        while self.current_token.type in ('PLUS', 'MINUS'):
            token = self.current_token
            debug_print(f"      加减运算符: {token.value}")
            self.eat(token.type)
            node = BinOpNode(node, token.value, self.term(), token.line_num)
            
        debug_print(f"      加减表达式解析结果: {node.__class__.__name__}")
        return node

    def term(self):
        """解析乘除表达式"""
        debug_print(f"        开始解析乘除表达式，位置: {self.pos}, 当前token: {self.current_token}")
        node = self.factor()
        
        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            token = self.current_token
            debug_print(f"        乘除运算符: {token.value}")
            self.eat(token.type)
            node = BinOpNode(node, token.value, self.factor(), token.line_num)
            
        debug_print(f"        乘除表达式解析结果: {node.__class__.__name__}")
        return node

    def factor(self):
        """解析因子"""
        debug_print(f"          开始解析因子，位置: {self.pos}, 当前token: {self.current_token}")
        token = self.current_token
        
        if token.type == 'LPAREN':
            debug_print(f"          左括号")
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            debug_print(f"          右括号")
            return node
        elif token.type in ('INTEGER', 'FLOAT'):
            debug_print(f"          数字: {token.value}")
            self.eat(token.type)
            return LiteralNode(token.value, token.line_num)
        elif token.type == 'STRING':
            debug_print(f"          字符串: {token.value}")
            self.eat('STRING')
            return LiteralNode(token.value, token.line_num)
        elif token.type == 'ID':
            debug_print(f"          标识符: {token.value}")
            self.eat('ID')
            return VarNode(token.value, token.line_num)
        else:
            self.error(f"无效的表达式: {token.value}") 