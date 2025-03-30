#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from core import DEBUG_MODE, debug_print
from core.lexer import Lexer
from core.parser import Parser
from core.interpreter import Interpreter
from core.errors import PinLangError

def run_code(code, file_name=None):
    """运行代码"""
    try:
        lexer = Lexer(code, file_name)
        
        if DEBUG_MODE:
            print("词法分析开始...")
        
        tokens = lexer.tokenize()
        
        if DEBUG_MODE:
            print(f"词法分析结果（{len(tokens)}个token）:")
            for i, token in enumerate(tokens):
                print(f"  {i}: {token}")
            print("\n语法分析开始...")
        
        parser = Parser(lexer, tokens)
        ast = parser.parse()
        
        if DEBUG_MODE:
            print(f"解析成功，生成了 {len(ast)} 个语句节点")
            print("\n解释执行开始...")
        
        interpreter = Interpreter(parser, file_name, ast)
        interpreter.interpret(ast)
    except KeyboardInterrupt:
        print("\n程序已中断")
        return False
    except PinLangError as e:
        print(e)
        return False
    except Exception as e:
        print(f"错误：{str(e)}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return False
    return True

def run_file(file_path):
    """运行文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        file_name = os.path.basename(file_path)
        
        if DEBUG_MODE:
            print(f"文件内容:\n{code}\n")
            print(f"正在执行文件: {file_name}")
            
        return run_code(code, file_name)
    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'")
        return False
    except Exception as e:
        print(f"错误：{str(e)}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        return False

def run_interactive():
    """运行交互式模式"""
    print("拼语言解释器 v1.0 - 交互模式")
    print("输入 'exit()' 退出")
    print("输入 'debug on' 开启调试模式")
    print("输入 'debug off' 关闭调试模式")
    
    while True:
        try:
            code = input('>>> ')
            
            if code.strip() == 'exit()':
                break
            elif code.strip() == 'debug on':
                import core
                core.DEBUG_MODE = True
                print("[调试模式已开启]")
                continue
            elif code.strip() == 'debug off':
                import core
                core.DEBUG_MODE = False
                print("[调试模式已关闭]")
                continue
                
            run_code(code)
        except KeyboardInterrupt:
            print("\n再见！")
            break
        except Exception as e:
            print(f"错误：{str(e)}")
            if DEBUG_MODE:
                import traceback
                traceback.print_exc()

def main():
    """主函数"""
    try:
        # 处理命令行参数
        debug_flag = False
        file_path = None
        test_loop = False  # 添加循环测试标志
        quiet_mode = True  # 默认安静模式，不显示版本信息
        
        for i, arg in enumerate(sys.argv[1:]):
            if arg == "--debug" or arg == "-d":
                debug_flag = True
                quiet_mode = False  # 调试模式时不使用安静模式
            elif arg == "--test-loop":
                test_loop = True
                quiet_mode = False
            elif arg == "--version" or arg == "-v":
                quiet_mode = False
            elif not file_path and not arg.startswith("-"):
                file_path = arg
        
        # 设置全局调试模式
        if debug_flag:
            import core
            core.DEBUG_MODE = True
        
        if not quiet_mode:
            print("拼语言解释器 v1.0")
            if debug_flag:
                print("[调试模式已开启]")
        
        # 测试循环功能
        if test_loop:
            # 强制开启调试模式
            import core
            core.DEBUG_MODE = True
            print("[正在测试循环功能，已强制开启调试模式]")
            
            # 创建测试文件
            test_file = "loop_test.pin"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("""# 循环测试
bl count = 0

# 标记循环点
dy('开始循环')
dy(count)

# 增加计数
jisuan count+1 = count

# 检查是否循环3次
panduan count = 3:
    dy('循环结束')
fouze:
    dy('继续循环')
    tiao ciwenjian hang=5  # 跳转到"开始循环"那一行
""")
            
            # 运行测试文件
            run_file(test_file)
            return
        
        if file_path:
            run_file(file_path)
        else:
            run_interactive()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")

if __name__ == '__main__':
    main() 