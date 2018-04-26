# !/usr/bin/env python
# -*- coding: utf-8 -*-
import xlrd
import os
import json

CONST_CONTENT_BEGIN = 5
CONST_EXECL_PATH = "./"
CONST_OUTPUT_PATH = './ouput'

def readExeclByGroup(findGroup,find,titles,types,sheet_data):
    table = {}
    main_group_col = sheet_data.col_values(findGroup)
    main_col = sheet_data.col_values(find)
    main_group_type = types[findGroup]
    main_type = types[find]
    for i in range(CONST_CONTENT_BEGIN,len(main_group_col)):
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
    return table

def readExeclByKey(find,titles,types,sheet_data):
    table = {}
    main_col = sheet_data.col_values(find)
    main_type = types[find]
    for i in range(CONST_CONTENT_BEGIN,len(main_col)):
        content = sheet_data.row_values(i)
        if main_col[i] != "":
            id = getValueByType(main_col[i],main_type)
            table[id] = {}
            for k in range(0,len(content)):
                if content[k] != '':
                    value = getValueByType(content[k],types[k])
                    key = titles[k]
                    table[id][key] = value
    return table

def readExeclNoKey(titles,types,sheet_data):
    table = []
    row_num = sheet_data.nrows
    for i in range(CONST_CONTENT_BEGIN,row_num):
        content = sheet_data.row_values(CONST_CONTENT_BEGIN)
        line = {}
        add = False
        for i in range(0,len(titles)):
            add = False
            if content[i] != "":
                add = True
                line[titles[i]] = getValueByType(content[i],types[i])
        if add:
            table.append(line)    
    if len(table) == 1:
        return table[0]
    return table

def readExecl(filename):
    ret = {}
    workbook = xlrd.open_workbook(filename)
    sheet_names= workbook.sheet_names()
    declare = {}
    for sheet in sheet_names:
        if sheet == '':
            continue
        outputs = sheet.split('|')
        sheet_name = outputs[0]
        single = False
        if sheet_name.startswith('#'):
            single = True
            sheet_name = sheet_name[1:]
        sheet_data = workbook.sheet_by_name(sheet)
        #拿到表头
        titles = sheet_data.row_values(1) 
        #拿到类型
        types = sheet_data.row_values(2) 
        findGroup = -1
        find = -1
        
        for i in range(0,len(titles)):
            title = titles[i]
            if title.startswith('*'):
                titles[i] = title[1:]
                find = i
            if title.startswith('#'):
                titles[i] = title[1:]
                findGroup = i

        if single:
            if findGroup != -1:
                if find != -1:
                    table = readExeclByGroup(findGroup,find,titles,types,sheet_data)
                    writeJsonFile(sheet_name+".json",table)
            elif find != -1:
                table = readExeclByKey(find,titles,types,sheet_data)
                writeJsonFile(sheet_name+".json",table)
            else :
                #都没有找到 为无key文件
                table = readExeclNoKey(titles,types,sheet_data)
                writeJsonFile(sheet_name+".json",table)
            continue

        #获得表头和类型的解析
        declare[sheet_name] = {}
        for i in range(0,len(titles)):
            declare[sheet_name][titles[i]] = change_type2str(types[i])   
        
        if findGroup != -1:
            if find != -1:
                ret[sheet_name] = readExeclByGroup(findGroup,find,titles,types,sheet_data)
        elif find != -1:
            ret[sheet_name] = readExeclByKey(find,titles,types,sheet_data)
        else :
            #都没有找到 为无key文件
            ret[sheet_name] = readExeclNoKey(titles,types,sheet_data)
    return ret,declare

def writeJsonFile(filename,data):
    data_str = json.dumps(data, sort_keys=True, indent=4,ensure_ascii=False)
    filePath = os.path.join(CONST_OUTPUT_PATH,filename)
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath,'w') as f:
        f.write(data_str)


def writeDeclareFile(filename,data):
    str = ""
    filePath = os.path.join(CONST_OUTPUT_PATH,filename)
    keys = data.keys()
    for sheet_name in keys:
        sheet_data = data[sheet_name]
        sheet_keys = sheet_data.keys()
        str += "declare interface C"+sheet_name.upper() + "{\n"
        for rowName in sheet_keys:
            rowType = sheet_data[rowName]
            str += "\t" + rowName + ":" + rowType + ",\n"
        str += "}\n"
            
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath,'w') as f:
        f.write(str)


def readPathFile(filePath):
    dic_table = {}
    dic_declare = {}
    listDir = os.listdir(filePath)
    for i in range(0,len(listDir)):
        subFilePath = os.path.join(filePath,listDir[i])
        if os.path.isfile(subFilePath):
            if file_extension(listDir[i]) == '.xlsx' or file_extension(listDir[i]) == '.xls':
                ret,declare = readExecl(subFilePath)
                dic_table.update(ret)
                dic_declare.update(declare)
        if os.path.isdir(subFilePath) and (not listDir[i].startswith('.')):
            ret,declare = readPathFile(subFilePath)
            dic_table.update(ret)
            dic_declare.update(declare)
    return dic_table,dic_declare

            
def file_extension(path): 
    return os.path.splitext(path)[1] 



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
    
def change_type2str(type1):
    if type1 == "int":
        return "number"
    if type1 == "float":
        return "number"
    if type1 == "str":
        return "string"
    if type1 == "array":
        return "any[]"
    if type1 == "json":
        return "{}"
    if type1 == "auto":
        return "any"
    return "any" 
    
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

def clearAllJsonFile(filePath):
    if os.path.exists(CONST_OUTPUT_PATH):
        #如果存在的话清空里面所有json文件
        list_files = os.listdir(CONST_OUTPUT_PATH)
        for i in range(0,len(list_files)):
            file = list_files[i]
            subfilePath = os.path.join(filePath,file)
            if os.path.isfile(subfilePath) and file_extension(file) == '.json':
                os.remove(subfilePath)
    else:
        os.makedirs(filePath)

if __name__ == '__main__':
    clearAllJsonFile(CONST_OUTPUT_PATH)
    dic_table,dic_declare = readPathFile(CONST_EXECL_PATH)
    writeJsonFile('mdata.json',dic_table)
    writeDeclareFile('tables.d.ts',dic_declare)
    
