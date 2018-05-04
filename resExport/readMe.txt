目标，导出资源，以及在资源后面加md5
步骤1，读取上次的default.res.json文件 主要是group部分，如果是九宫格需要在exml里配置
步骤2，读取各个目录的文件 生成对应的key和路径
 特殊目录有 sheet（纹理集）
 目录分类
    gui（界面相关，小元件，如果有纹理集还是放到sheet）
    movieclip (帧动画)
    armture (骨骼动画)
    sheet (纹理集)
    
