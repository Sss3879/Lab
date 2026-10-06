import yaml
import csv
import math

CONFIG_PATH = "config.yaml"

def load_config(config_path):
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_csv(csv_path, col_x, col_y):
    xs = []
    ys = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                xs.append(float(row[col_x]))
                ys.append(float(row[col_y]))
            except ValueError:
                raise ValueError("CSV contains non-numeric or empty values")
    return xs, ys

def calculate_correlation(xs, ys):
    """计算均值和 Pearson 相关系数"""

    n = len(xs)

    if n == 0:
        raise ValueError("CSV contains no data")

    if len(xs) != len(ys):
        raise ValueError("xs and ys must have the same length")

    sum_x = 0.0
    sum_y = 0.0
    for i in range(n):
        sum_x = sum_x + xs[i]
        sum_y = sum_y + ys[i]

    mean_x = sum_x / n
    mean_y = sum_y / n

    dx = 0.0
    dy = 0.0
    prod = 0.0
    for i in range(n):
        a = xs[i] - mean_x
        b = ys[i] - mean_y
        dx = dx + a * a
        dy = dy + b * b
        prod = prod + a * b
    
    denom = math.sqrt(dx * dy)
    if denom == 0:
        raise ValueError("Pearson correlation is undefined when a variable has zero variance.")
    r = prod / denom

    return mean_x, mean_y, r

def main():
    """程序主流程"""
    cfg = load_config(CONFIG_PATH)

    csv_path = cfg["input_csv"]
    col_x = cfg["columns"]["x"]
    col_y = cfg["columns"]["y"]

    xs, ys = load_csv(csv_path, col_x, col_y)

    mean_x, mean_y, r = calculate_correlation(xs, ys)

    print("n =", len(xs))
    print("mean_x =", mean_x)
    print("mean_y =", mean_y)
    print("r =", r)


if __name__ == "__main__":
    main()