#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 全局调试模式开关
DEBUG_MODE = False

def debug_print(*args, **kwargs):
    """调试打印函数，只在调试模式开启时打印"""
    global DEBUG_MODE
    if DEBUG_MODE:
        print(*args, **kwargs)

# 导入所有子模块
from core.errors import *
from core.tokens import *
from core.lexer import *
from core.ast import *
from core.parser import *
from core.interpreter import * 