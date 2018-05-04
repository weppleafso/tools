# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os,shutil
import json
import readMd5



CONST_EXT_TYPE = {
    '.png' : 'image',
    '.jpg' : 'image',
    '.json' : 'json',
    '.txt' : 'text',
    '.mp3': 'sound'
}
CONST_EXT_TYPE2 = {
    '.json' : 'sheet',
    '.fnt' : 'fnt'
}
CONST_EXT_DEFAULT = 'bin'

CONST_GUI_DIR = ['gui']

CONST_RSOURCE_DIR = './assets'
CONST_INPUT_RES = './default.res.json'
CONST_OUPUT_DIR = './ouput'
CONST_SHOW_EXT = True

#返回group部分
def readResfile(filePath):
    with open(filePath) as file:
        str_data = file.read()
        res = json.loads(str_data)
        return res['groups']

def export_gui_dir(dirPath,subDir):
    lists = os.listdir(dirPath)
    sheetJson = {}
    resJson = []
    makDir(os.path.join('assets',subDir))
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dirPath,item)
        if os.path.isdir(path):
            assetsPath = os.path.join(dirPath,item,'assets')
            print(assetsPath)
            if os.path.exists(assetsPath):
                export_all_res(assetsPath,os.path.join(subDir,item))

def export_all_res(dirPath,subDir):
    lists = os.listdir(dirPath)
    resJson = []
    makDir(os.path.join('assets',subDir))
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dirPath,item)
        if not item.startswith('.' ) and os.path.isfile(path):
            outDir = os.path.join('assets',subDir)
            cpFile(dirPath,outDir,item)   
    for i in range(0,len(lists)):
        item = lists[i]
        print(item)
        if os.path.isdir(path) and not item.startswith('.'):
            nextPath = os.path.join(dirPath,item)
            nowSubPath = os.path.join(subDir,item)
            if item in CONST_GUI_DIR:
                export_gui_dir(nextPath,nowSubPath)
            else:
                export_all_res(nextPath,nowSubPath)

def export_res_json(dirPath,subDir):
    lists = os.listdir(dirPath)
    sheetJson = {}
    resJson = []
    #找出所有的sheet或者font文件，并且记录下来
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dirPath,item)
        if os.path.isfile(path):
            name,ext = file_extension(item)
            print("xxxx",name)
            if ext == '.fnt' or ext == '.json':
                if isSheetOrFont(path):
                    sheetJson[name] = True

    #先输出所有文件
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dirPath,item)
        if os.path.isfile(path) and (not item.startswith('.')):
            name,ext = file_extension(item)
            filePath = path
            subType = 1
            keys = sheetJson.keys()
            if name in keys:
                subType = 2
            if ext == '.png' and subType == 2:
                continue
            fileType = get_file_type(ext,subType)
            #输出文件并且记录
            dic = {}
            dic['name'] = name + "_" + ext
            dic['type'] = fileType
            dic['url'] = os.path.join(subDir,item)
            if(ext == '.json' and subType == 2):
                dic['subkeys'] = readSheetSubKeys(filePath)
            resJson.append(dic)
    #处理所有的子文件夹
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dirPath,item)
        if os.path.isdir(path) and (not item.startswith('.')) :
            ret = export_res_json(os.path.join(dirPath,item),os.path.join(subDir,item))
            resJson.extend(ret)
    return resJson

def file_extension(path): 
    texts = os.path.splitext(path)
    return texts[0],texts[1]

def isSheetOrFont(filePath):
    with open(filePath) as file:
        mdata = json.loads(file.read())
        keys = mdata.keys()
        if 'file' in keys:
            #给文件流加上md5码
            return True
    return False

def readSheetSubKeys(filePath):
    with open(filePath) as file:
        mdata = json.loads(file.read())
        frames = mdata['frames']
        keys = frames.keys()
        subKeys = ""
        for i in range(0,len(keys)):
            subKeys += keys[i] + ','
        return subKeys[0:len(subKeys)-1]
    return None

def makDir(dirPath):
    outputDir = os.path.join(CONST_OUPUT_DIR,dirPath)
    os.mkdir(outputDir)

def cpFile(inDir,outDir,fileName):
    iFilePath = os.path.join(inDir,fileName)
    oFilePath = os.path.join(CONST_OUPUT_DIR,outDir,fileName)
    shutil.copyfile(iFilePath,oFilePath)


def get_file_type(ext,subType):
    if subType == 2:
        return CONST_EXT_TYPE2[ext]
    keys = CONST_EXT_TYPE.keys()
    if ext in keys:
        return CONST_EXT_TYPE[ext]
    return CONST_EXT_DEFAULT

#清理目录下的所有文件
def cleanDir(dir):
    lists = os.listdir(dir)
    for i in range(0,len(lists)):
        item = lists[i]
        path = os.path.join(dir,item)
        if not item.startswith('.') and os.path.isdir(path):
            cleanDir(path)
            if os.path.exists(path):
                os.removedirs(path)
        if os.path.isfile(path):
            os.remove(path)

def writeJsonFile(filename,data):
    data_str = json.dumps(data, sort_keys=True, indent=4,ensure_ascii=False)
    filePath = os.path.join(CONST_OUPUT_DIR,filename)
    if os.path.exists(filePath):
        os.remove(filePath)
    with open(filePath,'w') as f:
        f.write(data_str)


if __name__ == '__main__':
    if os.path.exists(CONST_OUPUT_DIR):
        cleanDir(CONST_OUPUT_DIR)
    os.mkdir(CONST_OUPUT_DIR)
       
    retGroup = readResfile(CONST_INPUT_RES)
    # print(ret)
    export_all_res(CONST_RSOURCE_DIR,'')
    retJson = export_res_json(os.path.join(CONST_OUPUT_DIR,'assets'),'assets')
    dic = {}
    dic['resources'] = retJson
    dic['groups'] = retGroup
    writeJsonFile('default.res.json',dic)

    



        