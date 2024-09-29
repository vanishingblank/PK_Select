import pandas as pd
import json
from datetime import datetime

# 读取特定工作表
file_path = './input.xlsx'
df = pd.read_excel(file_path, sheet_name='班级名单')  # 替换为你的工作表名称

# 假设 DataFrame 中的列名为 '组号', '组序号', '姓名', '学号'
# 你需要根据实际的列名进行调整
result = {}

# 遍历 DataFrame 的每一行
for index, row in df.iterrows():
    group_number = row['组号']  # 组号
    group_sequence = row['组序号']  # 组序号
    name = row['姓名']  # 姓名
    student_id = row['学号']  # 学号

    # 检查组号和组序号是否存在
    if pd.notna(group_number) and pd.notna(group_sequence):
        # 创建组号的字典，如果不存在则初始化
        if group_number not in result:
            result[group_number] = []

        # 添加学生信息到对应的组
        student_info = {
            "group id": group_sequence,  # 组序号
            "name": name,
            "student id": student_id,
            "shoot": True,  # 默认值为 True
            "program": True,  # 默认值为 True
            "absent": False #默认值为False
        }
        result[group_number].append(student_info)

# 对每个组内的学生信息按照组序号排序
for group_number in result:
    result[group_number].sort(key=lambda x: x["group id"])

# 按组号排序结果字典
sorted_result = dict(sorted(result.items(), key=lambda x: x[0]))

# 获取当前时间
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file_name = f"{current_time}.json"


# 将结果转换为 JSON 格式
json_output = json.dumps(sorted_result, ensure_ascii=False, indent=4)

# 输出到 TXT 文件
output_file_path = 'output.json'
with open(output_file_path, 'w', encoding='utf-8') as f:
    f.write(json_output)

print(f"数据已成功输出到 {output_file_path}")