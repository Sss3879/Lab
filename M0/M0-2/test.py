
from legacy_corr import calculate_correlation, load_csv
import tempfile
import os


def test_positive_correlation():
    print("\n===== 测试 1：正相关 =====")
    xs = [1, 2, 3]
    ys = [2, 4, 6]

    print("测试数据：")
    print("xs =", xs)
    print("ys =", ys)
    print("预期结果：r = 1.0")

    _, _, r = calculate_correlation(xs, ys)

    print("实际结果：r =", r)


def test_negative_correlation():
    print("\n===== 测试 2：负相关 =====")
    xs = [1, 2, 3]
    ys = [6, 4, 2]

    print("测试数据：")
    print("xs =", xs)
    print("ys =", ys)
    print("预期结果：r = -1.0")

    _, _, r = calculate_correlation(xs, ys)

    print("实际结果：r =", r)


def test_empty_data():
    print("\n===== 测试 3：空数据 =====")
    xs = []
    ys = []

    print("测试数据：")
    print("xs =", xs)
    print("ys =", ys)
    print("预期结果：抛出 ValueError")
    print("预期错误：CSV contains no data")

    try:
        calculate_correlation(xs, ys)
    except ValueError as e:
        print("实际结果：捕获到 ValueError")
        print("实际错误：", e)


def test_zero_variance():
    print("\n===== 测试 4：零方差 =====")
    xs = [1, 1, 1]
    ys = [2, 4, 6]

    print("测试数据：")
    print("xs =", xs)
    print("ys =", ys)
    print("预期结果：抛出 ValueError")
    print("预期错误：Pearson correlation is undefined when a variable has zero variance.")

    try:
        calculate_correlation(xs, ys)
    except ValueError as e:
        print("实际结果：捕获到 ValueError")
        print("实际错误：", e)


def test_missing_column():
    print("\n===== 测试 5：CSV 缺少列 =====")

    # 创建一个临时 CSV
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False
    ) as f:
        f.write("x,y\n")
        f.write("1,2\n")
        csv_path = f.name

    print("测试 CSV：")
    print("x,y")
    print("1,2")
    print("请求读取的列：height, y")
    print("预期结果：抛出 ValueError")
    print("预期错误：CSV column 'height' not found")

    try:
        # 读取不存在的 "height" 列
        load_csv(csv_path, "height", "y")
    except ValueError as e:
        print("实际结果：捕获到 ValueError")
        print("实际错误：", e)
    finally:
        os.remove(csv_path)
        print("临时 CSV 已删除")


if __name__ == "__main__":
    print("========== 开始单元测试 ==========")

    test_positive_correlation()
    test_negative_correlation()
    test_empty_data()
    test_zero_variance()
    test_missing_column()

    print("\n========== 测试结束 ==========")
