# -*- coding: utf-8 -*-

"""
@author: xansar
@software: PyCharm
@file: utils.py
@time: 2023/9/26 12:06
@e-mail: xansar@ruc.edu.cn
"""
import re

def construct_med_map_dict(drug_lst):
    # 使用正则表达式提取代码和序号
    pattern = r'(\d+)\. ([A-Z\d]+) -'
    matches = re.findall(pattern, drug_lst)

    # 创建一个双向映射的字典
    code_to_number = {code: int(number) - 1 for number, code in matches}
    number_to_code = {int(number) - 1: code for number, code in matches}
    return {
        'med2idx': code_to_number,
        'idx2med': number_to_code
    }