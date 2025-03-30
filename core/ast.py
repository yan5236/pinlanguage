#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AST节点类
class AST:
    """抽象语法树基类"""
    def __init__(self, line_num):
        self.line_num = line_num

class PrintNode(AST):
    """打印节点"""
    def __init__(self, value, line_num):
        super().__init__(line_num)
        self.value = value

class VarDeclNode(AST):
    """变量声明节点"""
    def __init__(self, var_name, value, line_num):
        super().__init__(line_num)
        self.var_name = var_name
        self.value = value

class VarNode(AST):
    """变量引用节点"""
    def __init__(self, var_name, line_num):
        super().__init__(line_num)
        self.var_name = var_name

class ListCreateNode(AST):
    """列表创建节点"""
    def __init__(self, var_name, values, line_num):
        super().__init__(line_num)
        self.var_name = var_name
        self.values = values

class ListGetNode(AST):
    """列表获取节点"""
    def __init__(self, list_name, index, target_var, line_num):
        super().__init__(line_num)
        self.list_name = list_name
        self.index = index
        self.target_var = target_var

class ListEditNode(AST):
    """列表编辑节点"""
    def __init__(self, list_name, index, value, line_num):
        super().__init__(line_num)
        self.list_name = list_name
        self.index = index
        self.value = value
    
    def __str__(self):
        return f"ListEditNode(list={self.list_name}, idx={self.index}, val={self.value})"

class CalculateNode(AST):
    """计算节点"""
    def __init__(self, expr, target_var, line_num):
        super().__init__(line_num)
        self.expr = expr
        self.target_var = target_var

class ConvertNode(AST):
    """类型转换节点"""
    def __init__(self, value, type_name, target_var, line_num):
        super().__init__(line_num)
        self.value = value
        self.type_name = type_name
        self.target_var = target_var

class IfNode(AST):
    """条件判断节点"""
    def __init__(self, condition, body, else_body, line_num):
        super().__init__(line_num)
        self.condition = condition
        self.body = body
        self.else_body = else_body

class LoopNode(AST):
    """循环节点"""
    def __init__(self, variable, condition, value, count, body, line_num):
        super().__init__(line_num)
        self.variable = variable     # 循环变量名，如果有的话
        self.condition = condition   # 循环条件（=, =!, >, <）
        self.value = value           # 循环条件的值
        self.count = count           # 循环次数
        self.body = body             # 循环体语句
    
    def __str__(self):
        return f"LoopNode(var={self.variable}, cond={self.condition}, val={self.value}, count={self.count}, body={len(self.body)} stmts)"

class InputNode(AST):
    """输入节点"""
    def __init__(self, prompt, target_var, restriction, line_num):
        super().__init__(line_num)
        self.prompt = prompt
        self.target_var = target_var
        self.restriction = restriction

class JumpNode(AST):
    """跳转节点"""
    def __init__(self, file_name, target_type, target_value, line_num):
        super().__init__(line_num)
        self.file_name = file_name
        self.target_type = target_type  # 'shuru' 或 'hang'
        self.target_value = target_value

class BinOpNode(AST):
    """二元操作节点"""
    def __init__(self, left, op, right, line_num):
        super().__init__(line_num)
        self.left = left
        self.op = op
        self.right = right

class LiteralNode(AST):
    """字面量节点"""
    def __init__(self, value, line_num):
        super().__init__(line_num)
        self.value = value

class LabelNode(AST):
    """标记点节点"""
    def __init__(self, label_name, line_num):
        super().__init__(line_num)
        self.label_name = label_name
    
    def __str__(self):
        return f"LabelNode({self.label_name})" 