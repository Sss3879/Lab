import json
from pathlib import Path
import yaml
from collections import deque
import math
import sys
import random
import time
import argparse

def load_config(path):
    """读取 JSON 或 YAML。"""
    path = Path(path)
    with path.open("r", encoding="utf-8") as file:
        if path.suffix.lower() == ".json":
            return json.load(file)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(file)
        raise ValueError("配置文件必须是 JSON 或 YAML")


def validate_tasks(config):
    """检查任务名、字段和依赖是否存在。"""
    if not isinstance(config, dict):
        raise ValueError("配置内容必须是字典")

    tasks = config.get("tasks")

    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks 必须是非空列表")

    names = set()

     # 第一遍：检查每个任务，收集所有任务名。
    for index, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError(f"第 {index} 个任务必须是字典")

        for field in ("name", "duration", "success_rate", "dependencies"):
            if field not in task:
                raise ValueError(f"第 {index} 个任务缺少字段：{field}")
        
        
        #任务名称判断
        name = task["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"第 {index} 个任务的 name 必须是非空字符串")

        if name in names:
            raise ValueError(f"任务名重复：{name}")

        names.add(name)


        # 对于任务的配置进行判断
        duration = task["duration"]

        if (
            isinstance(duration, bool)
            or not isinstance(duration, (int, float))
            or not math.isfinite(duration)
            or duration < 0
        ):
            raise ValueError(
                f"任务 {name} 的 duration 必须是非负的有限数值"
            )

        success_rate = task["success_rate"]

        if (
            isinstance(success_rate, bool)
            or not isinstance(success_rate, (int, float))
            or not 0 <= success_rate <= 1
        ):
            raise ValueError(
                f"任务 {name} 的 success_rate 必须是 0 到 1 之间的数值"
            )


        #对于依赖进行判断
        dependencies = task["dependencies"]
 
        if not isinstance(dependencies, list):
            raise ValueError(f"任务 {name} 的 dependencies 必须是列表")

        for dependency in dependencies:
            if not isinstance(dependency, str) or not dependency.strip():
                raise ValueError(f"任务 {name} 的依赖必须是非空字符串")


    # 第二遍：检查依赖的任务是否存在。
    for task in tasks:
        for dependency in task["dependencies"]:
            if dependency not in names:
                raise ValueError(
                    f"任务 {task['name']} 依赖不存在的任务：{dependency}"
                )

    return tasks

def topological_sort(tasks):
#     这段代码的作用是：
# 1. 从 ready 中取出一个可以执行的任务，加入执行顺序。
# 2. 通知依赖它的后续任务：“你的一个前置任务已经排好了。”
# 3. 如果某个后续任务的所有前置任务都排好了，就把它放进 ready。
# 4. 重复以上过程，直到队列为空。


    """返回合法执行顺序；存在环则报错。"""
    indegree = {}
    followers = {}

    # 1. 为每个任务准备记录。
    for task in tasks:
        name = task["name"]
        indegree[name] = 0
        followers[name] = []

    # 2. 记录依赖数量，以及每个任务的后续任务。
    for task in tasks:
        name = task["name"]

        for dependency in task["dependencies"]:
            indegree[name] += 1
            followers[dependency].append(name)

    # 3. 没有前置依赖的任务，先进入队列。
    ready = deque()

    for name in indegree:
        if indegree[name] == 0:
            ready.append(name)

    order = []

    # 4. 不断取出可以执行的任务。
    while ready:
        name = ready.popleft()
        order.append(name)

        for follower in followers[name]:
            indegree[follower] -= 1

            if indegree[follower] == 0:
                ready.append(follower)

    # 5. 如果还有任务没有排进去，说明存在环。
    if len(order) != len(tasks):
        raise ValueError("检测到依赖环，无法生成执行顺序")

    return order

def execute_tasks(tasks, order, timeout):
    """按依赖顺序模拟执行，返回包含全部任务的报告。"""

    started_at = time.monotonic()
    deadline = started_at + timeout

    # 建立“任务名 → 任务配置”的对应关系。
    task_map = {}
    records = {}

    for task in tasks:
        name = task["name"]
        task_map[name] = task
        records[name] = {
            "name": name,
            "status": None,
            "attempts": 0,
            "duration": 0.0,
            "started_at": None,
            "ended_at": None
        }

    timed_out = False

    for name in order:

        # 开始处理任务前，检查是否超时。
        if time.monotonic() >= deadline:
            timed_out = True
            break

        task = task_map[name]
        record = records[name]

        # 检查前置任务是否全部成功。
        blocked = False

        for dependency in task["dependencies"]:
            if records[dependency]["status"] != "SUCCESS":
                blocked = True
                break

        if blocked:
            record["status"] = "SKIPPED"
            print(f"SKIPPED：{name}，前置任务未成功", flush=True)
            continue

        # 最多尝试三次：首次执行 + 两次重试。
        for attempt in range(1, 4):

             # 每次尝试前，计算还剩多少时间。
            remaining = deadline - time.monotonic()
            
            if remaining <= 0:
                timed_out = True
                break

            record["attempts"] = attempt
            if attempt == 1:
                record["started_at"] = time.time()

            attempt_started = time.monotonic()
            print(
                f"执行：{name}，第 {attempt} 次尝试",
                flush=True
            )

            # 最多等待到截止时间。
            time.sleep(min(task["duration"], remaining))

            # 重试耗时也计入当前任务的实际耗时。
            record["duration"] += time.monotonic() - attempt_started
            record["ended_at"] = time.time()

            # 等待结束后，先检查是否超时。
            if time.monotonic() >= deadline:
                timed_out = True
                break

            if random.random() < task["success_rate"]:
                record["status"] = "SUCCESS"
                print(f"SUCCESS：{name}", flush=True)
                break

            print(f"FAILED：{name}", flush=True)

            if attempt < 3:
                print(f"RETRY：{name}", flush=True)
            else:
                record["status"] = "SKIPPED"
                print(
                    f"SKIPPED：{name}，三次尝试均失败",
                    flush=True
                )
        
         # 内层循环因超时退出后，外层循环也要退出。
        if timed_out:
            break
    
    if timed_out:
        print("TIMEOUT：全局时间已用完", flush=True)

        # 当前未完成的任务和未开始的任务都标记为超时。
        for name in order:
            if records[name]["status"] is None:
                records[name]["status"] = "TIMEOUT"
                print(f"TIMEOUT：{name}", flush=True)

    total_duration = time.monotonic() - started_at
    print(f"总耗时：{total_duration:.2f} 秒", flush=True)

    # 报告按配置中的顺序排列，保留未执行任务的记录。
    task_reports = []
    for task in tasks:
        task_reports.append(records[task["name"]])

    return {
        "timeout": timed_out,
        "total_duration": total_duration,
        "tasks": task_reports
    }

def main():
    parser = argparse.ArgumentParser(
        description="按依赖顺序模拟执行任务"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="配置文件路径，支持 JSON 或 YAML"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="全局超时秒数，覆盖配置文件中的 timeout"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机种子，用于复现模拟结果"
    )

    parser.add_argument(
        "--report",
        default="report.json",
        help="报告输出路径，默认 report.json"
    )

    args = parser.parse_args()

    try:
        config = load_config(args.config)
        tasks = validate_tasks(config)
        order = topological_sort(tasks)

        # 命令行指定了 timeout，就优先使用命令行的值。
        if args.timeout is not None:
            timeout = args.timeout
        else:
            timeout = config.get("timeout", 15)

        if (
            isinstance(timeout, bool)
            or not isinstance(timeout, (int, float))
            or not math.isfinite(timeout)
            or timeout <= 0
        ):
            raise ValueError("timeout 必须是大于 0 的有限数值")

        if args.seed is not None:
            random.seed(args.seed)

        report = execute_tasks(tasks, order, timeout)

        with open(args.report, "w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")

        print(f"报告已保存：{args.report}")

    except FileNotFoundError as error:
        print(
            f"错误：找不到文件：{error.filename}",
            file=sys.stderr
        )
        return 1

    except yaml.YAMLError as error:
        print(
            f"错误：YAML 格式不正确：{error}",
            file=sys.stderr
        )
        return 1

    except (OSError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
