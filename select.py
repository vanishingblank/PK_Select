import json
from datetime import datetime
import sys
import random

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
        # 检查该组所有学生的 program 属性
        all_program_false = all(not student["program"] for student in students)
        if all_program_false:
            for student in students:
                student["program"] = True  # 将该组所有学生的 program 属性设置为 True

        # 检查该组所有学生的 shoot 属性
        all_shoot_false = all(not student["shoot"] for student in students)
        if all_shoot_false:
            for student in students:
                student["shoot"] = True  # 将该组所有学生的 shoot 属性设置为 True

    # 将所有学生的 absent 属性设置为 False
    for group_id, students in data.items():
        for student in students:
            student['absent'] = False



def mark_absent(data, names_to_mark):
    valid_names = {student['name'] for group in data.values() for student in group}
    for name in names_to_mark:
        if name in valid_names:
            for group_id, students in data.items():
                for student in students:
                    if student['name'] == name:
                        student['absent'] = True
        else:
            print(f"警告: 名字 '{name}' 不在学生名单中。")



def select_programmers(data):
    selected_members = []
    for group_key, group in data.items():
        group_index = int(group_key.split('.')[0])
        eligible_members = [member for member in group if not member['absent'] and member['program']]

        if eligible_members:
            selected = eligible_members[0]
        else:
            # 如果没有合格的程序员，随机选择一个未缺席的学生
            eligible_members = [member for member in group if not member['absent']]
            if eligible_members:
                selected = random.choice(eligible_members)
            else:
                continue  # 如果组里没有未缺席的学生，跳过该组

        selected_members.append((group_index, selected))
        selected['program'] = False  # 将选中的学生的 program 属性设置为 False

    return selected_members



def write_results_to_file(selected_students, selected_photographers):
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{current_date}.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("测试要求\n")
        f.write("（1）参赛同学可以操作机器提交代码，其他同学只能围观，不能操作机器。\n")
        f.write("组号\t\t\t参赛同学\t\t\t学号\n")

        for group_index, student in selected_students:
            f.write(f"第{group_index}组\t\t{student['name']}\t\t{student['student id']}\n")

        f.write("（2）监督同学\n")
        f.write("①负责监督被监督小组做题过程中是否存在作弊行为\n")
        f.write("②拍一张被监督小组做题的照片，证明正在做题的情形，命名 \"小组PK1_组号_姓名.png\"\n")
        f.write("组号\t\t\t监督同学\t\t\t学号\t\t\t监督组号\n")

        for group_index, photographer in selected_photographers:
            f.write(
                f"第{group_index}组\t\t{photographer['name']}\t\t{photographer['student id']}\t\t{photographer['supervised group']}\n")

    print(f"结果已保存到 {filename}")


# 在 select_photographers 函数中添加监督组号

def select_photographers(data, selected_programmers):
    selected_photographers = []
    selected_programmer_names = {student['name'] for _, student in selected_programmers}  # 获取已选程序员的名字

    for group_key, group in data.items():
        group_index = int(group_key.split('.')[0])
        eligible_members = [member for member in group if not member['absent'] and member['shoot'] and member['name'] not in selected_programmer_names]

        if eligible_members:
            selected = eligible_members[0]
        else:
            # 如果没有合格的摄影师，随机选择一个未缺席的学生
            eligible_members = [member for member in group if not member['absent'] and member['name'] not in selected_programmer_names]
            if eligible_members:
                selected = random.choice(eligible_members)
            else:
                continue  # 如果组里没有未缺席的学生，跳过该组

        selected_photographers.append((group_index, selected))
        selected['shoot'] = False  # 将选中的学生的 shoot 属性设置为 False

    return selected_photographers


def main():
    filename = 'output.json'
    data = load_data(filename)

    if not data:
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

    selected_students = select_programmers(data)
    selected_photographers = select_photographers(data,selected_students)

    # 保存更新后的数据
    save_data(filename, data)

    write_results_to_file(selected_students, selected_photographers)
    print("")


if __name__ == "__main__":
    main()
