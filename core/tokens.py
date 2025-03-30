#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Token:
    """词法标记类"""
    def __init__(self, token_type, value, line_num):
        self.type = token_type
        self.value = value
        self.line_num = line_num

    def __str__(self):
        return f"Token({self.type}, {self.value}, 行:{self.line_num})" 