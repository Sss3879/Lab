3. 编写 README —— 问题报告
必须写清：

哪里有问题（定位到具体行/变量）
现象是什么（报什么错 / 结果哪里不对）
为什么会有问题（原理层面的原因）
怎么解决的
建议做成表格，逐条列出你发现的每个缺陷。


1. 变量名未统一

CSV 表头是：
time,value
但代码读取的是大写的 "Value"：
v = float(row["Value"])

2. 算法错误
2.1 标准差的计算：
for v in data:
    acc += (v - mean)
std = acc / len(data)
所有数据与均值的偏差之和理论上等于 0，所以这里算出的不是标准差。
解决： acc += (v - mean) ** 2
std = math.sqrt(acc / len(data))

2.2 离群值剔除

遍历 data 时又执行 data.remove(v)，会导致部分元素被跳过。
只剔除了过大的值，没有剔除过小的值。
cleaned 始终为空

解决：
for t, v in zip(times, data):
    if abs(v - mean) <= 2 * std:
        cleaned.append((t, v))

3. 清洗后数据存储路径！
运行代码后报错  
 File "/home/dev/Lab/M0/M0-3/sensor_analyzer.py", line 64, in <module>
    f = open(output_path, "w")
FileNotFoundError: [Errno 2] No such file or directory: '/out/cleaned_data.csv'
原因是：绝对路径不存在

解决：执行前先创建文件夹，再改为相对路径。

4. 写入清洗后的数据逻辑
原代码写入文件后没有关闭
f = open(output_path, "w")

解决：改用with open语法

异常处理：
