import json
from pathlib import Path
import yaml
from collections import deque
import math
import sys

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


def main():
    
    try:
        config = load_config("tasks_demo.yaml")
        tasks = validate_tasks(config)
        order = topological_sort(tasks)

    except FileNotFoundError as error:
        print(
            f"错误：找不到配置文件：{error.filename}",
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

    for name in order:
        print(name)

    return 0


if __name__ == "__main__":
    main()