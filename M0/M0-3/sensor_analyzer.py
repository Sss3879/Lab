#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensor_analyzer.py  —— 上一届学长留下的"能用"的脚本

注释（学长原话）：
    "处理一下传感器数据就能用"

原本意图：
    1. 读取 sensor_data.csv（列：time, value）
    2. 计算 value 的平均值、标准差
    3. 剔除离群值（|value - mean| > 2 * std）
    4. 把清洗后的数据保存为 cleaned_data.csv
    5. 打印一份统计摘要

现状：跑不通 / 跑出来数不对。就交给你了。
"""

import csv
import os
import math

INPUT_FILE = "sensor_data.csv"
OUTPUT_FILE = "cleaned_data.csv"
OUTPUT_DIR = "out"  # 输出目录
def main():

        
    data = []
    times = []
    cleaned = []

    print("=== 传感器数据分析 ===")

    # --- 读取数据 ---
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        #表头异常情况处理
        if not reader.fieldnames or not {"time", "value"} <= set(reader.fieldnames):
            raise ValueError("CSV 表头必须包含 time 和 value")


        for row in reader:
            t = row["time"]
            v = row["value"]

            #空内容的处理
            if t is None or not t.strip() or v is None or not str(v).strip():
                raise ValueError(f"第 {reader.line_num} 行的 time 或 value 为空")
            
            #value 不是数字的处理
            try:
                v = float(v)
            except ValueError as e:
                raise ValueError(f"第 {reader.line_num} 行的 value 不是数字") from e
           
            times.append(t)
            data.append(v)
            
    #空表格的处理
    if not data:
        raise ValueError("CSV 没有数据行")

    print("共读取 %d 条数据" % len(data))

    # --- 计算平均值 ---
    total = 0
    for v in data:
        total += v
    mean = total / len(data)

    # --- 计算标准差 ---
    acc = 0
    for v in data:
        acc += (v - mean)**2

    std =math. sqrt( acc / len(data))

    # --- 剔除离群值 ---
    for t , v in zip(times, data):
        if abs(v - mean) <= 2 * std:
            cleaned.append((t, v))

    # --- 输出清洗后的数据 ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join( OUTPUT_DIR, OUTPUT_FILE)

    with open(output_path, "w", newline="",  encoding="utf-8" ) as f:
        writer = csv.writer(f)
        writer.writerow(["time", "value"])
        for t, v in cleaned:
            writer.writerow([t, v])



    print("均值 mean = %.4f" % mean)
    print("标准差 std = %.4f" % std)
    print("清洗后剩余 %d 条" % len(cleaned))
    print("已保存到 %s" % output_path)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError, csv.Error) as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)