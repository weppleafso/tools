#规则要求 
1.文件名是没有任何作用的 表名可以用|隔开 例如test|测试表1 如果想输出单个文件的可以使用在前面加#号的方式 例如 #test2|测试表2 这时候就会导出test2.json了 其他的都会输出到mdata.json中
2.内容格式
1）第一行为策划的表头 中英文均可
2）第二行为程序的表头 只支持英文字母 加*表示这一列为一级key 加#表示这一列为二级key
只有一级key的模式为
{
  id:{内容}
}
有二级key的模式为
{
  group:{id:{内容}}
}
3）第三列为类型 现在支持的类型有int（整数） float（浮点数） str（字符串） array（数组）以及json（字典），整数和浮点数要区分开，因为有精度丢失的问题
4）第四行为策划自己备注
5）从第六行起为策划的配置内容

3.输出文件
mdata.json 为输出的总文件
tables.d.ts 为前端使用导表出来的引用文件，方便做强类型检查
单个文件 ：例如昵称注册这种只会在注册时使用的文件可以输出单个，例如test24.json这种

4.待实现，可以使用输出的时候进行表格检查以及表格优化，这个待定
