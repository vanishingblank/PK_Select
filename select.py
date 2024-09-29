import json
from datetime import datetime
import sys  # 导入 sys 模块

def load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件 {filename} 未找到，请检查路径。")
        return {}
    except json.JSONDecodeError:
        print(f"文件 {filename} 不是有效的 JSON 格式。")
        return {}


def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_students(data):
    for group_id, students in data.items():
        all_false = all(not (student["shoot"] or student["program"]) for student in students)

        if all_false:
            for student in students:
                student["shoot"] = True
                student["program"] = True

    for group_id, students in data.items():
        for student in students:
            student['absent'] = False

def mark_absent(data, names_to_mark):
    for group_id, students in data.items():
        for student in students:
            if student['name'] in names_to_mark:
                student['absent'] = True


def select_programmers(data):
    selected_members = []
    for group_key, group in data.items():
        group_index = int(group_key.split('.')[0])
        eligible_members = [member for member in group if not member['absent'] and member['program']]
        if eligible_members:
            selected = eligible_members[0]
            selected_members.append((group_index, selected))
            # 将选中的学生的 program 属性设置为 False
            selected['program'] = False
    return selected_members


def write_results_to_file(selected_students):
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{current_date}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("组号\t参赛同学\t学号\n")
        for group_index, student in selected_students:  # 提取元组中的组号和学生信息
            # 假设 'student id' 是字典中的一个键，否则你需要替换为正确的键
            if 'student id' in student:  # 确保 'student id' 键存在
                f.write(f"{group_index}\t{student['name']}\t{student['student id']}\n")
            else:
                f.write(f"{group_index}\t{student['name']}\tN/A\n")  # 如果 'student id' 不存在，则输出 N/A

    print(f"结果已保存到 {filename}")


def main():
    filename = 'output.json'

    data = load_data(filename)
    if not data:  # 如果 data 是 {}，则结束程序
        print("没有加载到有效的数据，程序结束。")
        sys.exit()

    update_students(data)
    save_data(filename, data)
    print("运行成功，数据初始化完成")

    names_to_mark = []
    print("有人缺席了吗？请输入人名，输入 'end' 结束：")

    while True:
        name = input()
        if name.lower() == 'end':
            break
        names_to_mark.append(name)

    mark_absent(data, names_to_mark)
    save_data(filename, data)
    print("已更新 absent 属性。")

    selected_students = select_programmers(data)  # 只调用一次
    save_data(filename, data)  # 保存更新后的 program 属性
    write_results_to_file(selected_students)
    # 这里不需要再次保存数据到文件，因为前面已经保存过了
    #print("")


if __name__ == "__main__":
    main()


