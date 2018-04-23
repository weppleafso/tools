# !/usr/bin/env python
# -*- coding: utf-8 -*-
import xlrd
import os
import json

def readExecl(filename):
    print(filename)
    ret = {}
    workbook = xlrd.open_workbook(filename)
    sheet_names= workbook.sheet_names()
    for sheet in sheet_names:
        outputs = sheet.split('|')
        sheet_name = outputs[0]
        sheet_data = workbook.sheet_by_name(sheet)
        #拿到表头
        titles = sheet_data.row_values(1) 
        #拿到类型
        types = sheet_data.row_values(2) 
        find = -1
        table = {}
        print(titles)
        for i in range(0,len(titles)):
            title = titles[i]
            if title.startswith('*'):
                titles[i] = title[1:]
                find = i
        if find != -1:
            main_col = sheet_data.col_values(find)
            main_type = types[find]
            for i in range(4,len(main_col)):
                content = sheet_data.row_values(i)
                id = getValueByType(main_col[i],main_type)
                table[id] = {}
                for k in range(0,len(content)):
                    if content[k] != '':
                        value = getValueByType(content[k],types[k])
                        key = titles[k]
                        table[id][key] = value
        ret[sheet_name] = table
    print(ret)
    return ret

def getValueByType(value,type1):
    if type1 == "int":
        return int(value)
    if type1 == "float":
        return float(value)
    if type1 == "array":
        return json.loads(value)
    if type1 == "json":
        return json.loads(value)
        
    return value  



if __name__ == '__main__':
    readExecl("test.xlsx")
    
