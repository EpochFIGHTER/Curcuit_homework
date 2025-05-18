#引用后可正常计算 适用于RLC分析
import math
import numpy as np
def build_A(node_0, node_1, node_2, node_3, frequency=1000):
    '''
    @brief 构建自导纳矩阵A应用于RLC电路分析
    '''
    global OMEGA
    OMEGA = 2 * math.pi * frequency

    # 节点映射表
    node_pairs = [
        (node_0, node_1),
        (node_0, node_2),
        (node_0, node_3),
        (node_1, node_2),
        (node_1, node_3),
        (node_2, node_3)
    ]

    # 计算各支路的导纳
    branch_admittances = {}
    for n1, n2 in node_pairs:
        branch = n1.branches.get(n2)  # 使用字典的get方法
        if branch and branch.Z != complex(0, 0):
            branch_admittances[(n1, n2)] = branch.Y
        else:
            branch_admittances[(n1, n2)] = complex(0, 0)

    # 自导纳计算
    a11 = branch_admittances[(node_0, node_1)] + branch_admittances[(node_1, node_2)] + branch_admittances[(node_1, node_3)]
    a22 = branch_admittances[(node_0, node_2)] + branch_admittances[(node_1, node_2)] + branch_admittances[(node_2, node_3)]
    a33 = branch_admittances[(node_0, node_3)] + branch_admittances[(node_1, node_3)] + branch_admittances[(node_2, node_3)]

    # 互导纳计算
    a12 = branch_admittances[(node_1, node_2)]
    a13 = branch_admittances[(node_1, node_3)]
    a23 = branch_admittances[(node_2, node_3)]

    A = np.array([[a11, -a12, -a13],
                  [-a12, a22, -a23],
                  [-a13, -a23, a33]])
    return A