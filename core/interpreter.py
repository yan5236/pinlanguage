#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from core.ast import *
from core.errors import PinLangRuntimeError, PinLangTypeError
from core import debug_print

class JumpResult:
    """跳转结果类，用于保存跳转目标信息"""
    def __init__(self, target_name):
        self.target_name = target_name
        
    def __str__(self):
        return f"JumpResult(target='{self.target_name}')"
        
    def __repr__(self):
        return self.__str__()

class Interpreter:
    """解释器"""
    def __init__(self, parser, file_name=None, ast=None):
        self.parser = parser
        self.file_name = file_name
        self.variables = {}
        self.ast = ast if ast is not None else parser.parse()
        self.current_line = 0
        self.statements = []
        self.jump_targets = {}  # 存储跳转目标
        
    def error(self, message, line_num=None):
        """报告运行时错误"""
        if line_num is None and self.current_line < len(self.statements):
            line_num = self.statements[self.current_line].line_num
        raise PinLangRuntimeError(message, line_num, self.file_name)
    
    def type_error(self, message, line_num=None, fix_suggestion=None):
        """报告类型错误"""
        if line_num is None and self.current_line < len(self.statements):
            line_num = self.statements[self.current_line].line_num
        raise PinLangTypeError(message, line_num, self.file_name, fix_suggestion)
    
    def initialize(self):
        """初始化解释器"""
        self.statements = self.ast
        
        # 预处理跳转目标
        debug_print("预处理跳转目标:")
        shuru_count = 0
        
        for i, stmt in enumerate(self.statements):
            if isinstance(stmt, InputNode):
                # 为输入语句添加索引，从0开始
                key = f"shuru_{shuru_count}"
                self.jump_targets[key] = i
                debug_print(f"  添加输入语句跳转目标: {key} -> 语句索引 {i}")
                shuru_count += 1
                
            # 添加行号跳转目标
            line_key = f"hang_{stmt.line_num}"
            self.jump_targets[line_key] = i
            debug_print(f"  添加行号跳转目标: {line_key} -> 语句索引 {i}")
        
        debug_print(f"预处理完成，共有 {len(self.jump_targets)} 个跳转目标")
    
    def execute_node(self, node):
        """执行单个节点"""
        if isinstance(node, PrintNode):
            return self.execute_print(node)
        elif isinstance(node, VarDeclNode):
            return self.execute_var_decl(node)
        elif isinstance(node, ListCreateNode):
            return self.execute_list_create(node)
        elif isinstance(node, ListGetNode):
            return self.execute_list_get(node)
        elif isinstance(node, CalculateNode):
            return self.execute_calculate(node)
        elif isinstance(node, ConvertNode):
            return self.execute_convert(node)
        elif isinstance(node, IfNode):
            return self.execute_if(node)
        elif isinstance(node, LoopNode):
            return self.execute_loop(node)
        elif isinstance(node, InputNode):
            return self.execute_input(node)
        elif isinstance(node, JumpNode):
            return self.execute_jump(node)
        elif isinstance(node, LiteralNode):
            return node.value
        elif isinstance(node, VarNode):
            return self.execute_var(node)
        elif isinstance(node, BinOpNode):
            return self.execute_binop(node)
        else:
            self.error(f"未实现的节点类型: {type(node).__name__}")
    
    def execute_print(self, node):
        """执行打印节点"""
        try:
            value = self.execute_node(node.value)
            print(value)  # 无论是否处于调试模式，都应该打印
            return None
        except Exception as e:
            print(f"打印错误: {str(e)}")
            self.error(f"打印时发生错误: {str(e)}", node.line_num)
    
    def execute_var_decl(self, node):
        """执行变量声明节点"""
        value = self.execute_node(node.value)
        self.variables[node.var_name] = value
        return None
    
    def execute_var(self, node):
        """执行变量引用节点"""
        var_name = node.var_name
        if var_name not in self.variables:
            self.error(f"未定义的变量: {var_name}", node.line_num)
        return self.variables[var_name]
    
    def execute_list_create(self, node):
        """执行列表创建节点"""
        values = [self.execute_node(value) for value in node.values]
        self.variables[node.var_name] = values
        return None
    
    def execute_list_get(self, node):
        """执行列表获取节点"""
        list_name = node.list_name
        if list_name not in self.variables:
            self.error(f"未定义的列表: {list_name}", node.line_num)
        
        lst = self.variables[list_name]
        if not isinstance(lst, list):
            self.error(f"{list_name} 不是一个列表", node.line_num)
        
        index = self.execute_node(node.index) if isinstance(node.index, AST) else node.index
        if not isinstance(index, int):
            self.error(f"列表索引必须是整数，但得到了 {type(index).__name__}", node.line_num)
        
        if index < 0 or index >= len(lst):
            self.error(f"列表索引越界: {index}, 列表长度: {len(lst)}", node.line_num)
        
        value = lst[index]
        self.variables[node.target_var] = value
        return None
    
    def execute_calculate(self, node):
        """执行计算节点"""
        try:
            result = self.execute_node(node.expr)
            self.variables[node.target_var] = result
            return None
        except TypeError as e:
            self.type_error(f"计算错误: {str(e)}", node.line_num)
    
    def execute_convert(self, node):
        """执行类型转换节点"""
        if node.value not in self.variables:
            self.error(f"未定义的变量: {node.value}", node.line_num)
        
        value = self.variables[node.value]
        
        if node.type_name == 'shuzi':
            try:
                if isinstance(value, str):
                    if value.isdigit():
                        result = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        result = float(value)
                    else:
                        self.error(f"无法将字符串 '{value}' 转换为数字", node.line_num)
                else:
                    result = float(value)
                    if result.is_integer():
                        result = int(result)
            except ValueError:
                self.error(f"无法将 {value} 转换为数字", node.line_num)
        elif node.type_name == 'zifu':
            result = str(value)
        else:
            self.error(f"未知的类型名: {node.type_name}", node.line_num)
        
        self.variables[node.target_var] = result
        return None
    
    def execute_if(self, node):
        """执行条件判断节点"""
        debug_print(f"执行条件判断，条件: {node.condition.__class__.__name__}")
        condition = self.execute_node(node.condition)
        debug_print(f"条件结果: {condition}，类型: {type(condition).__name__}")
        
        if condition:
            debug_print(f"条件为真，执行if主体，共 {len(node.body)} 个语句")
            for i, stmt in enumerate(node.body):
                debug_print(f"执行if主体语句 {i+1}: {stmt.__class__.__name__}")
                result = self.execute_statement(stmt)
                if isinstance(result, JumpResult):
                    return result
        else:
            debug_print(f"条件为假，执行else主体，共 {len(node.else_body)} 个语句")
            for i, stmt in enumerate(node.else_body):
                debug_print(f"执行else主体语句 {i+1}: {stmt.__class__.__name__}")
                result = self.execute_statement(stmt)
                if isinstance(result, JumpResult):
                    return result
        
        return None
    
    def execute_input(self, node):
        """执行输入节点"""
        prompt = node.prompt
        
        # 处理可选的限制
        restriction = node.restriction
        if restriction == 'zifu':
            # 如果限制输入为数字，禁止字符输入
            while True:
                try:
                    user_input = input(prompt)
                    if user_input.replace('.', '', 1).isdigit():
                        # 如果是整数
                        if user_input.isdigit():
                            result = int(user_input)
                        else:
                            result = float(user_input)
                        break
                    else:
                        print("错误：请输入数字")
                except ValueError:
                    print("错误：请输入有效数字")
        else:
            # 没有限制，接受任何输入
            user_input = input(prompt)
            result = user_input
        
        self.variables[node.target_var] = result
        return None
    
    def execute_jump(self, node):
        """执行跳转语句"""
        debug_print(f"执行跳转语句: {node}")
        
        if node.file_name == 'current':
            file_name = self.file_name
        else:
            # 处理其他文件跳转（未实现）
            file_name = node.file_name
            raise PinLangRuntimeError("暂不支持跨文件跳转", node.line_num)
        
        # 根据跳转类型确定目标
        if node.target_type == 'label':
            target_name = node.target_value
        elif node.target_type == 'hang':
            target_name = f"hang_{node.target_value}"
        elif node.target_type == 'shuru':
            target_name = f"shuru_{node.target_value}"
        else:
            raise PinLangRuntimeError(f"未知的跳转类型: {node.target_type}", node.line_num)
        
        debug_print(f"  跳转目标名称: {target_name}")
        
        # 返回跳转结果
        return JumpResult(target_name)
    
    def execute_binop(self, node):
        """执行二元操作节点"""
        debug_print(f"执行二元操作，操作符: {node.op}")
        left = self.execute_node(node.left)
        right = self.execute_node(node.right)
        
        debug_print(f"  左操作数: {left} (类型: {type(left).__name__})")
        debug_print(f"  右操作数: {right} (类型: {type(right).__name__})")
        
        if node.op == '+':
            if (isinstance(left, (int, float)) and isinstance(right, (int, float))) or (isinstance(left, str) and isinstance(right, str)):
                result = left + right
                debug_print(f"  加法结果: {result}")
                return result
            else:
                self.type_error(f"{type(left).__name__}类型不可与{type(right).__name__}类型进行加法操作", 
                                node.line_num, 
                                f"需要zhuanhuan 变量 shuzi = zifu 或相反")
        elif node.op == '-':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = left - right
                debug_print(f"  减法结果: {result}")
                return result
            else:
                self.type_error("只有数字可以进行减法操作", node.line_num)
        elif node.op == '*':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = left * right
                debug_print(f"  乘法结果: {result}")
                return result
            elif isinstance(left, str) and isinstance(right, int):
                result = left * right
                debug_print(f"  字符串重复结果: {result}")
                return result
            elif isinstance(left, int) and isinstance(right, str):
                result = left * right
                debug_print(f"  字符串重复结果: {result}")
                return result
            else:
                self.type_error("乘法操作符需要兼容的类型", node.line_num)
        elif node.op == '/':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if right == 0:
                    self.error("除数不能为零", node.line_num)
                result = left / right
                debug_print(f"  除法结果: {result}")
                return result
            else:
                self.type_error("只有数字可以进行除法操作", node.line_num)
        elif node.op == '>':
            result = left > right
            debug_print(f"  大于比较结果: {result}")
            return result
        elif node.op == '<':
            result = left < right
            debug_print(f"  小于比较结果: {result}")
            return result
        elif node.op == '>=':
            result = left >= right
            debug_print(f"  大于等于比较结果: {result}")
            return result
        elif node.op == '<=':
            result = left <= right
            debug_print(f"  小于等于比较结果: {result}")
            return result
        elif node.op == '=':
            result = left == right
            debug_print(f"  等于比较结果: {result}")
            return result
        elif node.op == '=!':
            result = left != right
            debug_print(f"  不等于比较结果: {result}")
            return result
        else:
            self.error(f"未支持的操作符: {node.op}", node.line_num)
    
    def execute_loop(self, node):
        """执行循环节点"""
        debug_print(f"执行循环，变量: {node.variable}, 条件: {node.condition}, 值: {node.value}, 次数: {node.count}")

        # 确定循环次数
        loop_count = 0
        if node.count is not None:
            if isinstance(node.count, int) or isinstance(node.count, float):
                loop_count = int(node.count)
                debug_print(f"  循环次数直接指定为: {loop_count}")
            else:
                count_value = self.execute_node(node.count)
                if isinstance(count_value, (int, float)):
                    loop_count = int(count_value)
                    debug_print(f"  循环次数通过变量指定为: {loop_count}")
                else:
                    self.error(f"循环次数必须是数字，但得到了 {type(count_value).__name__}", node.line_num)
        
        # 处理条件循环
        max_iterations = 10000  # 防止无限循环
        iteration_count = 0
        
        # 循环条件判断函数
        def check_condition():
            if node.variable is None or node.condition is None or node.value is None:
                return iteration_count < loop_count  # 只根据次数循环
                
            # 获取变量值
            var_value = self.variables.get(node.variable)
            if var_value is None:
                self.error(f"未定义的循环变量: {node.variable}", node.line_num)
            
            # 获取比较值
            compare_value = node.value
            if isinstance(compare_value, AST):
                compare_value = self.execute_node(compare_value)
            
            # 根据条件类型比较
            if node.condition == '=':
                return var_value == compare_value
            elif node.condition == '=!':
                return var_value != compare_value
            elif node.condition == '>':
                return var_value > compare_value
            elif node.condition == '<':
                return var_value < compare_value
            elif node.condition == '>=':
                return var_value >= compare_value
            elif node.condition == '<=':
                return var_value <= compare_value
            else:
                self.error(f"未知的循环条件: {node.condition}", node.line_num)
        
        # 执行循环
        while check_condition() and iteration_count < max_iterations:
            debug_print(f"  执行第 {iteration_count+1} 次循环")
            iteration_count += 1
            
            # 执行循环体
            for i, stmt in enumerate(node.body):
                debug_print(f"    执行循环体语句 {i+1}: {stmt.__class__.__name__}")
                result = self.execute_statement(stmt)
                if isinstance(result, JumpResult):
                    debug_print(f"    循环体中返回跳转: {result}")
                    return result
            
            # 如果没有指定循环条件，只根据次数循环
            if node.variable is None or node.condition is None or node.value is None:
                if iteration_count >= loop_count:
                    break
        
        if iteration_count >= max_iterations:
            print(f"警告: 可能存在无限循环，已执行 {max_iterations} 次迭代后停止")
        
        debug_print(f"循环执行完成，共执行了 {iteration_count} 次")
        return None

    def execute_statement(self, stmt):
        """执行单个语句"""
        if isinstance(stmt, PrintNode):
            self.execute_print(stmt)
        elif isinstance(stmt, VarDeclNode):
            self.execute_var_decl(stmt)
        elif isinstance(stmt, ListCreateNode):
            self.execute_list_create(stmt)
        elif isinstance(stmt, ListGetNode):
            self.execute_list_get(stmt)
        elif isinstance(stmt, ListEditNode):
            self.execute_list_edit(stmt)
        elif isinstance(stmt, CalculateNode):
            self.execute_calculate(stmt)
        elif isinstance(stmt, ConvertNode):
            self.execute_convert(stmt)
        elif isinstance(stmt, IfNode):
            return self.execute_if(stmt)  # 返回可能的跳转结果
        elif isinstance(stmt, LoopNode):
            return self.execute_loop(stmt)  # 返回可能的跳转结果
        elif isinstance(stmt, InputNode):
            self.execute_input(stmt)
        elif isinstance(stmt, JumpNode):
            return self.execute_jump(stmt)
        elif isinstance(stmt, LabelNode):
            # 标记点不需要执行任何操作
            pass
        else:
            # 其他语句类型处理
            debug_print(f"未知的语句类型: {type(stmt).__name__}")
        
        # 默认返回None（非跳转）
        return None

    def execute_list_edit(self, node):
        """执行列表编辑节点"""
        list_name = node.list_name
        if list_name not in self.variables:
            self.error(f"未定义的列表: {list_name}", node.line_num)
        
        lst = self.variables[list_name]
        if not isinstance(lst, list):
            self.error(f"{list_name} 不是一个列表", node.line_num)
        
        index = self.execute_node(node.index) if isinstance(node.index, AST) else node.index
        if not isinstance(index, int):
            self.error(f"列表索引必须是整数，但得到了 {type(index).__name__}", node.line_num)
        
        if index < 0 or index >= len(lst):
            self.error(f"列表索引越界: {index}, 列表长度: {len(lst)}", node.line_num)
        
        # 执行值节点，获取要设置的值
        value = self.execute_node(node.value)
        
        # 修改列表的指定元素
        lst[index] = value
        
        # 更新变量表中的列表
        self.variables[list_name] = lst
        
        return None

    def interpret(self, statements):
        """解释执行语句列表"""
        debug_print("解释执行开始...")
        
        # 预处理跳转目标
        debug_print("预处理跳转目标:")
        jump_targets = {}
        shuru_count = 0
        
        for idx, stmt in enumerate(statements):
            if isinstance(stmt, LabelNode):
                target_name = stmt.label_name
                debug_print(f"  添加标签跳转目标: {target_name} -> 语句索引 {idx}")
                jump_targets[target_name] = idx
            
            # 处理输入语句跳转目标
            if isinstance(stmt, InputNode):
                target_name = f"shuru_{shuru_count}"
                debug_print(f"  添加输入语句跳转目标: {target_name} -> 语句索引 {idx}")
                jump_targets[target_name] = idx
                shuru_count += 1
            
            # 处理行号跳转目标
            line_num = stmt.line_num
            target_name = f"hang_{line_num}"
            debug_print(f"  添加行号跳转目标: {target_name} -> 语句索引 {idx}")
            jump_targets[target_name] = idx
        
        debug_print(f"预处理完成，共有 {len(jump_targets)} 个跳转目标")
        
        self.jump_targets = jump_targets
        
        # 初始化解释器状态
        debug_print(f"解释器初始化完成，共 {len(statements)} 个语句")
        
        # 执行语句列表
        current_idx = 0
        max_iterations = 1000  # 防止无限循环
        iteration_count = 0
        
        while current_idx < len(statements) and iteration_count < max_iterations:
            iteration_count += 1
            
            if current_idx >= len(statements):
                break
            
            stmt = statements[current_idx]
            debug_print(f"执行语句 {current_idx+1}/{len(statements)}: {stmt.__class__.__name__} (迭代 {iteration_count})")
            
            try:
                # 执行当前语句
                result = self.execute_statement(stmt)
                
                # 处理跳转指令
                if isinstance(result, JumpResult):
                    debug_print(f"  跳转指令: {result}")
                    
                    # 查找跳转目标
                    if result.target_name in self.jump_targets:
                        new_idx = self.jump_targets[result.target_name]
                        debug_print(f"  找到跳转目标 '{result.target_name}' -> 语句索引 {new_idx}")
                        debug_print(f"  当前索引从 {current_idx} 变更为 {new_idx}")
                        current_idx = new_idx
                        continue  # 跳过递增计数器
                    else:
                        avail_targets = ', '.join(self.jump_targets.keys())
                        error_msg = f"找不到跳转目标 '{result.target_name}'，可用目标: {avail_targets}"
                        raise PinLangRuntimeError(error_msg, stmt.line_num)
                
                # 继续到下一条语句
                current_idx += 1
                
            except PinLangRuntimeError as e:
                # 运行时错误
                print(e)
                break
            except Exception as e:
                # 未知错误
                print(f"未知错误: {e}")
                if hasattr(debug_print, '__self__') and debug_print.__self__.DEBUG_MODE:
                    import traceback
                    traceback.print_exc()
                break
        
        if iteration_count >= max_iterations:
            print(f"警告: 可能存在无限循环，已执行 {max_iterations} 次迭代后停止") 