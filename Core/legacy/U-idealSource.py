# 引入numpy库
import numpy as np

# 四个节点，总共会有6种类型的连接关系
# 假设从端口输入进来的数据为一个列表,则设列表中有6个元素,分别为1——2,1——3,1——4,2——3,2——4,3——4
# 选4号节点电压为参考电压,默认正值为左大于右（例如最后一个元素中3>4）
information = [[1+2j,2+1j],[3+4j],[5+6j],[7+8j],[{"IVS":3+2j},3+4j],[{"IVS":5},3+4j]]

# 建立节点电压法矩阵运算关系式
# 求自导纳和互导纳
total1 = 0
total2 = 0
total3 = 0
total12 = sum(x for x in information[0] if isinstance(x, (int, float, complex)))
total13 = sum(x for x in information[1] if isinstance(x, (int, float, complex)))
total23 = sum(x for x in information[3] if isinstance(x, (int, float, complex)))

for num in (0,1,2):
    total1 += sum(x for x in information[num] if isinstance(x, (int, float, complex)))

for num in (0,3,4):
    total2 += sum(x for x in information[num] if isinstance(x, (int, float, complex)))

for num in (1,3,5):
    total3 += sum(x for x in information[num] if isinstance(x, (int, float, complex)))

# 建立导纳矩阵
Y=np.array([[total1,-total12,-total13],[-total12,total2,-total23],[-total13,-total23,total3]])

# 建立电流矩阵
S=np.array([[0],[0],[0]])

# 找到独立电压源的位置
def find_ivs(lst):
    results = []
    for i, sublist in enumerate(lst):
        for element in sublist:
            if isinstance(element, dict) and "IVS" in element:
                results.append((i + 1, element["IVS"]))  # 索引+1转换为人类计数
    return results

# 针对不同位置的独立电压源设定导纳矩阵的系数
A = {1:[1,-1,0],2:[1,0,-1],3:[1,0,0],4:[0,1,-1],5:[0,1,0],6:[0,0,1]}

# 扩展导纳矩阵和电流矩阵
for t in find_ivs(information):

    # 获取当前Y矩阵的列数
    cols = Y.shape[1]

    # 判断需要添加的行矩阵的元素个数
    if cols-3>0 :
        A[t[0]].extend([0] * (cols-3))

    # 转为 1 行 cols 列的矩阵
    matrix1 = np.array(A[t[0]]).reshape(1, cols)

    # 添加一行
    Y = np.r_[Y, matrix1]

    # 建立空矩阵
    B = []
    # 获取当前Y矩阵的行数
    rows = Y.shape[0]
    # 设置当前需要添加的列矩阵的元素个数
    B.extend([0] * rows)
    # 添加一列
    Y = np.c_[Y, B]

    # 将电压源的值导入一个列表中
    matrix2 = [t[1]]

    # 转为 1 行 cols 列的矩阵
    matrix2 = np.array(matrix2).reshape(1, 1)

    # 给电流矩阵添加一行
    S = np.r_[S,matrix2]

# 使用 np.linalg.lstsq 求解最小二乘解
x, residuals, rank, s = np.linalg.lstsq(Y, S, rcond=None)

# 输出计算的结果
# print(x)

# 最终运行结果去前三个即为1、2、3号节点的电压
for i in (0,1,2):
    print(x[i])