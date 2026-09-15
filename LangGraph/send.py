from typing import Annotated, List, Sequence, TypedDict
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send

# 定义状态
class DiliState(TypedDict):
    subjects: List[str]
    jokes: Annotated[List[str], lambda x, y: x + y]  # 使用列表合并的方式

# class DiliState(TypedDict):
#     subjects: List[str]
#     jokes: Annotated[List[str], lambda x, y: x+y]

# 第一个节点：生成需要处理的主题列表
def generate_subjects(state: DiliState) -> dict:
    """生成需要处理的主题列表"""
    print("执行节点(第一个节点：生成需要处理的主题列表): generate_subjects")
    subjects = ["猫", "狗", "程序员"]
    print(f"生成主题列表: {subjects}")
    return {"subjects": subjects}


# Map节点：为每个主题生成笑话
def make_joke(state: DiliState) -> dict:
    """为单个主题生成笑话"""
    subject = state.get("subject", "未知")
    print(f"执行节点: make_joke，处理主题: {subject}")

    # 根据主题生成相应笑话
    jokes_map = {
        "猫": "为什么猫不喜欢在线购物？因为它们更喜欢实体店！",
        "狗": "为什么狗不喜欢计算机？因为它们害怕被鼠标咬！",
        "程序员": "为什么程序员喜欢洗衣服？因为他们在寻找bugs！",
        "未知": "这是一个关于未知主题的神秘笑话。",
    }

    joke = jokes_map.get(subject, f"这是一个关于{subject}的即兴笑话。")
    print(f"生成笑话: {joke}")
    return {"jokes": [joke]}


# 条件边函数：根据主题列表生成Send对象列表
def map_subjects_to_jokes(state: DiliState) -> List[Send]:
    """将主题列表映射到joke生成任务"""
    print("执行条件边函数: map_subjects_to_jokes")
    subjects = state["subjects"]
    print(f"映射主题到joke任务: {subjects}")

    # 为每个主题创建一个Send对象，指向make_joke节点
    # 每个Send对象包含节点名称和传递给该节点的状态
    send_list = [Send("make_joke", {"subject": subject})
                 for subject in subjects]
    print(f"生成Send对象列表: {send_list}")
    return send_list

def main():
    """演示Map-Reduce模式"""
    print("=== Map-Reduce 模式演示 ===\n")

    # 创建图
    builder = StateGraph(DiliState)

    # 添加节点
    builder.add_node("generate_subjects", generate_subjects)
    builder.add_node("make_joke", make_joke)

    # 添加边
    builder.add_edge(START, "generate_subjects")

    # 添加条件边，使用Send对象实现map-reduce
    builder.add_conditional_edges(
        "generate_subjects",  # 源节点
        map_subjects_to_jokes,  # 路由函数，返回Send对象列表
    )

    # 从make_joke到结束
    builder.add_edge("make_joke", END)

    # 编译图
    graph = builder.compile()
    print(graph.get_graph().print_ascii())

    # 执行图
    initial_state = {"subjects": [], "jokes": []}
    print("初始状态:", initial_state)
    print("\n开始执行图...")

    result = graph.invoke(initial_state)
    print(f"\n最终结果: {result}")

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()

"""
【输出示例】
=== Map-Reduce 模式演示 ===

    +-----------+      
    | __start__ |      
    +-----------+      
          *            
          *            
          *            
+-------------------+  
| generate_subjects |  
+-------------------+  
          *            
          *            
          *            
     +---------+       
     | __end__ |       
     +---------+       
None
初始状态: {'subjects': [], 'jokes': []}

开始执行图...
执行节点(第一个节点：生成需要处理的主题列表): generate_subjects
生成主题列表: ['猫', '狗', '程序员']
执行条件边函数: map_subjects_to_jokes
映射主题到joke任务: ['猫', '狗', '程序员']
生成Send对象列表: [Send(node='make_joke', arg={'subject': '猫'}), Send(node='make_joke', arg={'subject': '狗'}), Send(node='make_joke', arg={'subject': '程序员'})]
执行节点: make_joke，处理主题: 猫
生成笑话: 为什么猫不喜欢在线购物？因为它们更喜欢实体店！
执行节点: make_joke，处理主题: 狗
生成笑话: 为什么狗不喜欢计算机？因为它们害怕被鼠标咬！
执行节点: make_joke，处理主题: 程序员
生成笑话: 为什么程序员喜欢洗衣服？因为他们在寻找bugs！

最终结果: {'subjects': ['猫', '狗', '程序员'], 'jokes': ['为什么猫不喜欢在线购物？因为它们更喜欢实体店！', '为什么狗不喜欢计算机？因为它们害怕被鼠标咬！', '为什么程序员喜欢洗衣服？因为他们在寻找bugs！']}

=== 演示完成 ===
"""
