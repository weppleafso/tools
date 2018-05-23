# !/usr/bin/env python
# -*- coding: utf-8 -*-
import xlrd
import os
import json


CONST_TITLE_POS = 1
CONST_TYPE_POS = 2
CONST_SUBTYPE_POS = 3
CONST_CONTENT_BEGIN = 5
CONST_EXECL_PATH = "./"
CONST_OUTPUT_PATH = './ouput'
CONST_KEYS_TABLE = ['const']

def readExeclByGroup(findGroup,find,titles,types,subTypes,sheet_data):
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
                for k in range(0,len(types)):
                    if types[k] != '':
                        value = getValueByType(content[k],types[k],subTypes[k])
                        key = titles[k]
                        table[group][id][key] = value  
    return table

def readExeclByKey(find,titles,types,subTypes,sheet_data):
    table = {}
    main_col = sheet_data.col_values(find)
    main_type = types[find]
    for i in range(CONST_CONTENT_BEGIN,len(main_col)):
        content = sheet_data.row_values(i)
        if main_col[i] != "":
            id = getValueByType(main_col[i],main_type)
            table[id] = {}
            for k in range(0,len(types)):
                if types[k] != '':
                    value = getValueByType(content[k],types[k],subTypes[k])
                    key = titles[k]
                    table[id][key] = value
    return table

def readExeclNoKey(titles,types,subTypes,sheet_data):
    table = []
    row_num = sheet_data.nrows
    for i in range(CONST_CONTENT_BEGIN,row_num):
        content = sheet_data.row_values(i)
        line = {}
        add = False
        if len(titles) == 1:
            k = 0
            table.append(getValueByType(content[k],types[k],subTypes[k]))   
        else:
            for k in range(0,len(titles)):
                add = False
                if types[k] != "":
                    add = True
                    line[titles[k]] = getValueByType(content[k],types[k],subTypes[k])
        if add:
            table.append(line)    
    if len(table) == 1:
        return table[0]
    return table

def readExecl(filename):
    ret = {}
    workbook = xlrd.open_workbook(filename)
    sheet_names= workbook.sheet_names()
    print(sheet_names)
    declare = {}
    for sheet in sheet_names:
        if sheet == '':
            continue
        outputs = sheet.split('|')
        if len(outputs) <= 1:
            continue
        sheet_name = outputs[0]
        print("导出子表格-----",sheet_name)
        single = False
        if sheet_name.startswith('#'):
            single = True
            sheet_name = sheet_name[1:]
        sheet_data = workbook.sheet_by_name(sheet)
        #拿到表头
        titles = sheet_data.row_values(CONST_TITLE_POS) 
        #拿到类型
        types = sheet_data.row_values(CONST_TYPE_POS) 
        #拿到子类型备注
        subTypes = sheet_data.row_values(CONST_SUBTYPE_POS)
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
                    table = readExeclByGroup(findGroup,find,titles,types,subTypes,sheet_data)
                    writeJsonFile(sheet_name+".json",table)
            elif find != -1:
                table = readExeclByKey(find,titles,types,subTypes,sheet_data)
                writeJsonFile(sheet_name+".json",table)
            else :
                #都没有找到 为无key文件
                table = readExeclNoKey(titles,types,subTypes,sheet_data)
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
            
            if (not listDir[i].startswith('~$')) and (file_extension(listDir[i]) == '.xlsx' or file_extension(listDir[i]) == '.xls'):
                print("开始导表<<<<<",subFilePath)
                ret,declare = readExecl(subFilePath)
                dic_table.update(ret)
                dic_declare.update(declare)
                print("导表结束>>>>>",subFilePath)
        if os.path.isdir(subFilePath) and (not listDir[i].startswith('.')):
            ret,declare = readPathFile(subFilePath)
            dic_table.update(ret)
            dic_declare.update(declare)
    return dic_table,dic_declare

            
def file_extension(path): 
    return os.path.splitext(path)[1] 



def getValueByType(value,type1,subType=None):
    if value == 'null':
        return None
    if type1 == "int":
        return int(value)
    if type1 == "float":
        return float(value)
    if type1 == "bool":
        if value == "true":
            return True
        return False
    if type1 == "array":
        try:
            lists = json.loads(value)
            if isinstance(lists,list):
                return lists
            return [lists]
        except ValueError:
            value = '['+value +']'
            return json.loads(value)
    if type1 == "json":
        if subType:
            tiles = subType.split(',')
            strs = value.split(';')
            ret = []
            for i in range(0,len(strs)):
                dic = {}
                contents = strs[i].split(',')
                for j in range(0,len(tiles)):
                    print(contents[j])
                    dic[tiles[j]] = getValueByType(contents[j],"auto",None)
                ret.append(dic)
            return ret
        else:
            return json.loads(value)
        
    if type1 == "auto":
        if is_digit(value):
            return int(value)
        if is_num(value):
            return float(value)
        if is_json(value):
            return json.loads(value)
        return "" + value
    return str(value)  
    
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
    if type1 == "bool":
        return "bool"
    if type1 == "auto":
        return "any"
    return "any" 
    
def is_json(text):
    try:
        json_object = json.loads(text)
    except ValueError:
        return False
    return True

def is_digit(text):
    ret = str(text)
    strs = ret.split('.')
    if len(strs) == 2:
        try:
            if float(ret) == int(strs[0]):
                return True
            return False
        except ValueError:
            return False
    return ret.isdigit()

def is_num(text):
    try:
        float(text)
    except ValueError:
        return False
    return True

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
    
