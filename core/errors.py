#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class PinLangError(Exception):
    """拼语言错误基类"""
    def __init__(self, message, line_num=None, file_name=None):
        self.message = message
        self.line_num = line_num
        self.file_name = file_name

    def __str__(self):
        error_loc = ""
        if self.file_name:
            error_loc += f"文件 {self.file_name}"
        if self.line_num is not None:
            error_loc += f"，第{self.line_num}行"
        if error_loc:
            return f"错误，{error_loc}\n错误原因：{self.message}"
        return f"错误：{self.message}"

class PinLangTypeError(PinLangError):
    """拼语言类型错误"""
    def __init__(self, message, line_num=None, file_name=None, fix_suggestion=None):
        super().__init__(message, line_num, file_name)
        self.fix_suggestion = fix_suggestion

    def __str__(self):
        error_str = super().__str__()
        if self.fix_suggestion:
            error_str += f"\n建议修复：{self.fix_suggestion}"
        return error_str

class PinLangSyntaxError(PinLangError):
    """拼语言语法错误"""
    pass

class PinLangRuntimeError(PinLangError):
    """拼语言运行时错误"""
    pass 