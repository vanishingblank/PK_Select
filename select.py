import json
from datetime import datetime
import sys
import random
import os

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
                        student['absent times'] += 1
        else:
            print(f"警告: 名字 '{name}' 不在学生名单中。")




def select_programmers(data):
    selected_members = []
    all_eligible_members = []  # 用于存储所有组的未缺席学生

    # 首先收集所有组的未缺席学生
    for group_key, group in data.items():
        eligible_members = [member for member in group if not member['absent']]
        all_eligible_members.extend(eligible_members)

    for group_key, group in data.items():
        group_index = int(group_key.split('.')[0])
        eligible_members = [member for member in group if not member['absent'] and member['program']]

        if eligible_members:
            selected = eligible_members[0]
        else:
            # 如果没有合格的程序员，选择 absent times 最大的学生
            eligible_members = [member for member in group if not member['absent']]
            if eligible_members:
                max_absent_times = max(member.get('absent times', 0) for member in eligible_members)
                candidates = [member for member in eligible_members if member.get('absent times', 0) == max_absent_times]
                selected = random.choice(candidates)  # 随机选择一个
            else:
                # 如果组里没有未缺席的学生，从其他组中选择
                if all_eligible_members:
                    selected = random.choice(all_eligible_members)  # 从所有未缺席的学生中随机选择
                else:
                    continue  # 如果没有未缺席的学生，跳过该组

        selected_members.append((group_index, selected))
        selected['program'] = False  # 将选中的学生的 program 属性设置为 False
        selected['absent times'] = 0
    return selected_members



def write_results_to_file(selected_students, selected_photographers,pk_num):
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
        f.write(f"②拍一张被监督小组做题的照片，证明正在做题的情形，命名 \"小组PK{pk_num}_组号_姓名.png\"\n")
        f.write("组号\t\t\t监督同学\t\t\t学号\t\t\t监督组号\n")

        for group_index, photographer in selected_photographers:
            f.write(
                f"第{group_index}组\t\t{photographer['name']}\t\t{photographer['student id']}\t\t{photographer['supervised group']}\n")

    print(f"结果已保存到 {filename}")


# 在 select_photographers 函数中添加监督组号


def select_photographers(data, selected_programmers):
    selected_photographers = []
    selected_programmer_names = {student['name'] for _, student in selected_programmers}  # 获取已选程序员的名字
    all_eligible_members = []  # 用于存储所有组的未缺席学生

    # 首先收集所有组的未缺席学生
    for group_key, group in data.items():
        eligible_members = [member for member in group if not member['absent'] and member['name'] not in selected_programmer_names]
        all_eligible_members.extend(eligible_members)

    for group_key, group in data.items():
        group_index = int(group_key.split('.')[0])
        eligible_members = [member for member in group if not member['absent'] and member['shoot'] and member['name'] not in selected_programmer_names]

        if eligible_members:
            selected = eligible_members[0]
        else:
            # 如果没有合格的摄影师，选择 absent times 最大的学生
            eligible_members = [member for member in group if not member['absent'] and member['name'] not in selected_programmer_names]
            if eligible_members:
                max_absent_times = max(member.get('absent times', 0) for member in eligible_members)
                candidates = [member for member in eligible_members if member.get('absent times', 0) == max_absent_times]
                selected = random.choice(candidates)  # 随机选择一个
            else:
                # 如果组里没有未缺席的学生，从其他组中选择
                if all_eligible_members:
                    selected = random.choice(all_eligible_members)  # 从所有未缺席的学生中随机选择
                else:
                    continue  # 如果没有未缺席的学生，跳过该组

        selected_photographers.append((group_index, selected))
        selected['shoot'] = False  # 将选中的学生的 shoot 属性设置为 False
        if selected['absent times'] > 0:
            selected['absent times'] -= 1
    return selected_photographers


def backup_data(filename, data, pk_num, class_number):
    # 根据班级数选择备份文件夹
    if class_number == '1':
        backup_folder = '241-1备份'
    elif class_number == '2':
        backup_folder = '241-2备份'
    else:
        print("无效的班级数，无法保存备份。")
        return

    # 确保备份文件夹存在
    os.makedirs(backup_folder, exist_ok=True)

    # 创建备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 格式化时间戳
    backup_filename = os.path.join(backup_folder,
                                   f"{os.path.splitext(os.path.basename(filename))[0]}_PK{pk_num}_{timestamp}.json")

    # 备份当前数据
    try:
        with open(backup_filename, 'w', encoding='utf-8') as backup_file:
            json.dump(data, backup_file, ensure_ascii=False, indent=4)
        print(f"备份已保存到 {backup_filename}")
    except Exception as e:
        print(f"备份文件保存失败: {e}")


def write_absent_students_to_file(data, pk_num, class_number):
    # 获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")

    # 根据班级号选择文件名
    if class_number == '1':
        filename = 'class_241-1_absent.txt'
    elif class_number == '2':
        filename = 'class_241-2_absent.txt'
    else:
        print("无效的班级号，无法写入缺席学生信息。")
        return

    # 打开文件以追加模式写入
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"PK 第 {pk_num} 次缺席学生记录 - 日期: {current_date}\n")
        for group_id, students in data.items():
            absent_students = [student['name'] for student in students if student['absent']]
            if absent_students:
                f.write(f"组 {group_id}: {', '.join(absent_students)}\n")
        f.write("\n")  # 添加一个空行以便于分隔不同的记录

    print(f"缺席学生信息已写入 {filename}")



def main():
    class_number = input("请输入上课班级（1 或 2）：")
    if class_number == '1':
        filename = '241-1.json'
    elif class_number == '2':
        filename = '241-2.json'
    else:
        input("无效的班级输入，程序结束。")
        sys.exit()

    pk_num = input("请输入这是第几次PK：")

    data = load_data(filename)

    if not data:
        print("没有加载到有效的数据，程序结束。")
        input("")
        sys.exit()

    # 在更新数据之前进行备份
    backup_data(filename, data, pk_num, class_number)

    update_students(data)
    save_data(filename, data)
    print("运行成功，数据初始化完成")

    names_to_mark = []
    valid_names = {student['name'] for group in data.values() for student in group}  # 获取所有有效的学生名字
    print("有人缺席了吗？请输入人名，输入 'end' 结束：")

    while True:
        name = input()
        if name.lower() == 'end':
            break
        if name in valid_names:
            names_to_mark.append(name)
        else:
            print(f"警告: 名字 '{name}' 不在学生名单中。")


    mark_absent(data, names_to_mark)
    save_data(filename, data)
    write_absent_students_to_file(data, pk_num, class_number)
    print("已更新 absent 属性。")

    selected_students = select_programmers(data)
    selected_photographers = select_photographers(data,selected_students)

    # 保存更新后的数据
    save_data(filename, data)



    write_results_to_file(selected_students, selected_photographers,pk_num)
    print("")
    input("")


if __name__ == "__main__":
    main()
