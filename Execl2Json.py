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
        findGroup = -1
        find = -1
        table = {}
        for i in range(0,len(titles)):
            title = titles[i]
            print(title)
            if title.startswith('*'):
                titles[i] = title[1:]
                find = i
            if title.startswith('#'):
                titles[i] = title[1:]
                findGroup = i
        if findGroup != -1:
            if find != -1:
                main_group_col = sheet_data.col_values(findGroup)
                main_col = sheet_data.col_values(find)
                main_group_type = types[findGroup]
                main_type = types[find]
                for i in range(4,len(main_group_col)):
                    content = sheet_data.row_values(i)
                    if main_group_col[i] != "":
                        group = getValueByType(main_group_col[i],main_group_type)
                        if not group in table.keys():
                            table[group] = {}
                        id = getValueByType(main_col[i],main_type)
                        table[group][id] = {}
                        for k in range(0,len(content)):
                            if content[k] != '':
                                value = getValueByType(content[k],types[k])
                                key = titles[k]
                                table[group][id][key] = value
        elif find != -1:
            main_col = sheet_data.col_values(find)
            main_type = types[find]
            for i in range(4,len(main_col)):
                content = sheet_data.row_values(i)
                if main_col[i] != "":
                    id = getValueByType(main_col[i],main_type)
                    table[id] = {}
                    for k in range(0,len(content)):
                        if content[k] != '':
                            value = getValueByType(content[k],types[k])
                            key = titles[k]
                            table[id][key] = value
            
        ret[sheet_name] = table
    return ret

def writeFile(filePath,data):
    data_str = json.dumps(data, sort_keys=True, indent=2,ensure_ascii=False)
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath,'w') as f:
        f.write(data_str)


def getValueByType(value,type1):
    if type1 == "int":
        return int(value)
    if type1 == "float":
        return float(value)
    if type1 == "array":
        return json.loads(value)
    if type1 == "json":
        return json.loads(value)
    if type1 == "auto":
        if is_digit(value):
            return int(value)
        if is_num(value):
            return float(value)
        if is_json(value):
            return json.loads(value)
        return "" + value
    return "" + value  
    
def is_json(text):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True

def is_digit(text):
    ret = "" + text
    return ret.isdigit()

def is_num(text):
    ret = "" + text
    return ret.isalnum()

if __name__ == '__main__':
    ret = readExecl("test.xlsx")
    writeFile('mdata.json',ret)
    
