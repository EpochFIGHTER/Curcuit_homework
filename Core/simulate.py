"""
四节点电路仿真主模块 - 完整实现修正节点分析法(MNA)
支持：
- 四节点电路网络
- 多元件串联
- 多支路并联
- 独立电压源/电流源
- 受控电压源/电流源
- RLC元件
"""
import numpy as np
import math
from Component import ElectricalNode, ElectricalComponent, ElectricalBranch
from Component import PowerSource, IndependentVoltageSource, IndependentCurrentSource
from Component import DependentVoltageSource, DependentCurrentSource

def get_nodes_and_voltage_sources(nodes):
    """
    获取电路中的所有节点(除参考节点外)和电压源
    
    参数:
        nodes: 所有节点列表，nodes[0]为参考节点
        
    返回:
        real_nodes: 除参考节点外的节点列表
        voltage_sources: 电路中所有电压源列表（独立+受控）
        dependent_sources: 电路中所有受控源列表（电压+电流）
    """
    # 提取除参考节点外的所有节点
    real_nodes = nodes[1:]
    
    # 创建空列表以存储电压源和受控源
    voltage_sources = []
    dependent_sources = []
    
    # 遍历所有节点对，查找电压源和受控源
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            # 获取连接节点i和j的所有支路
            branches = nodes[i].branches.get(nodes[j], [])
            
            # 遍历每个支路，查找电源
            for branch in branches:
                for component in branch:
                    # 检查是否为独立电压源
                    if isinstance(component, IndependentVoltageSource):
                        voltage_sources.append((branch, component))
                    
                    # 检查是否为受控电压源
                    elif isinstance(component, DependentVoltageSource):
                        voltage_sources.append((branch, component))
                        dependent_sources.append(component)
                    
                    # 检查是否为受控电流源
                    elif isinstance(component, DependentCurrentSource):
                        dependent_sources.append(component)
    
    return real_nodes, voltage_sources, dependent_sources

def build_mna_matrix(nodes, frequency=1000):
    """
    构建修正节点分析法(MNA)矩阵方程：Ax = b
    
    参数:
        nodes: 所有节点列表，nodes[0]为参考节点
        frequency: 频率，默认1000Hz
        
    返回:
        A: MNA系数矩阵
        b: MNA右端向量
        mapping: 未知量映射字典，记录每个未知量在解向量中的索引
    """
    # 设置电路频率
    from Component import set_freq
    set_freq(frequency)
    
    # 获取除参考节点外的节点和所有电压源
    nodes_no_ref, voltage_sources, dependent_sources = get_nodes_and_voltage_sources(nodes)
    
    # MNA矩阵的大小
    n_nodes = len(nodes_no_ref)  # 非参考节点数量
    n_vsrc = len(voltage_sources)  # 电压源数量
    n = n_nodes + n_vsrc  # 总未知量数量
    
    # 构造MNA矩阵和右端向量
    A = np.zeros((n, n), dtype=complex)
    b = np.zeros(n, dtype=complex)
    
    # 创建未知量映射
    mapping = {}
    for i, node in enumerate(nodes_no_ref):
        mapping[node] = i  # 节点电压在解向量中的位置
    for i, (branch, _) in enumerate(voltage_sources):
        mapping[branch] = n_nodes + i  # 电压源电流在解向量中的位置
    
    # 构建导纳矩阵（G子矩阵）部分
    # 遍历所有节点对
    for i in range(len(nodes)):
        node_i = nodes[i]
        
        for j in range(i + 1, len(nodes)):
            node_j = nodes[j]
            
            # 获取两节点间的所有支路
            branches = node_i.branches.get(node_j, [])
            
            # 跳过没有连接的节点对
            if not branches:
                continue
            
            # 处理每条支路
            for branch in branches:
                # 跳过包含电压源的支路，它们稍后处理
                if any(isinstance(component, (IndependentVoltageSource, DependentVoltageSource)) 
                       for component in branch):
                    continue
                
                # 计算支路导纳
                if branch.Z != 0:
                    Y = branch.Y
                else:
                    Y = 0
                
                # 找到支路中的电流源（如果有）
                current_source = None
                for component in branch:
                    if isinstance(component, IndependentCurrentSource):
                        current_source = component
                        break
                    elif isinstance(component, DependentCurrentSource):
                        current_source = component
                        break
                
                # 更新导纳矩阵和电流向量
                # 节点i和j的行列索引（参考节点的导纳被自动忽略）
                i_idx = mapping.get(node_i) if i > 0 else None
                j_idx = mapping.get(node_j) if j > 0 else None
                
                # 更新导纳矩阵（支路导纳）
                if Y != 0:
                    if i_idx is not None:
                        A[i_idx, i_idx] += Y  # 节点i的自导纳
                        if j_idx is not None:
                            A[i_idx, j_idx] -= Y  # 节点i-j的互导纳
                    
                    if j_idx is not None:
                        A[j_idx, j_idx] += Y  # 节点j的自导纳
                        if i_idx is not None:
                            A[j_idx, i_idx] -= Y  # 节点j-i的互导纳
                
                # 更新电流向量（独立电流源）
                if current_source and isinstance(current_source, IndependentCurrentSource):
                    I = current_source.I
                    if i_idx is not None:
                        b[i_idx] -= I  # 流入节点i的电流为负
                    if j_idx is not None:
                        b[j_idx] += I  # 流出节点j的电流为正
    
    # 处理电压源约束（B和C子矩阵）
    for idx, (branch, vsrc) in enumerate(voltage_sources):
        # 电压源支路的两个节点
        node1, node2 = branch.node_left, branch.node_right
        
        # 源节点的索引
        i_idx = mapping.get(node1) if node1 != nodes[0] else None
        j_idx = mapping.get(node2) if node2 != nodes[0] else None
        
        # 电压源电流的索引
        v_idx = n_nodes + idx
        
        # B子矩阵（电压源电流对节点方程的贡献）
        if i_idx is not None:
            A[i_idx, v_idx] += 1  # 节点i处流入的电流
        if j_idx is not None:
            A[j_idx, v_idx] -= 1  # 节点j处流出的电流
        
        # C子矩阵（节点电压对电压源方程的贡献）
        if i_idx is not None:
            A[v_idx, i_idx] += 1  # KVL：v_i
        if j_idx is not None:
            A[v_idx, j_idx] -= 1  # KVL：-v_j
        
        # 更新电压源方程右端向量
        if isinstance(vsrc, IndependentVoltageSource):
            b[v_idx] = vsrc.U  # 独立电压源值
    
    # 处理受控源约束
    for dep_src in dependent_sources:
        # 获取受控源所在支路
        branch = dep_src.branch
        
        # 获取控制元件所在支路
        ctrl_branch = dep_src.controler.branch
        
        # 获取控制元件的源节点索引
        if ctrl_branch in mapping:
            ctrl_idx = mapping[ctrl_branch]
        else:
            # 如果控制元件不在映射中，则跳过
            continue
        
        # 受控源类型处理
        if isinstance(dep_src, DependentVoltageSource):
            # 获取受控电压源约束方程的索引
            for i, (br, _) in enumerate(voltage_sources):
                if br == branch:
                    v_idx = n_nodes + i
                    break
            
            # 根据控制量类型更新矩阵
            if dep_src.value == "U":
                # 控制元件的电压作为控制量
                ctrl_node1 = ctrl_branch.node_left
                ctrl_node2 = ctrl_branch.node_right
                
                # 控制节点索引
                ci_idx = mapping.get(ctrl_node1) if ctrl_node1 != nodes[0] else None
                cj_idx = mapping.get(ctrl_node2) if ctrl_node2 != nodes[0] else None
                
                # 电压控制电压源（VCVS）约束：v_out = k * v_control
                if ci_idx is not None:
                    A[v_idx, ci_idx] -= dep_src.k
                if cj_idx is not None:
                    A[v_idx, cj_idx] += dep_src.k
                
            elif dep_src.value == "I":
                # 控制元件的电流作为控制量
                # 电流控制电压源（CCVS）约束：v_out = k * i_control
                A[v_idx, ctrl_idx] -= dep_src.k
        
        elif isinstance(dep_src, DependentCurrentSource):
            # 获取受控电流源所在的节点索引
            node1, node2 = branch.node_left, branch.node_right
            i_idx = mapping.get(node1) if node1 != nodes[0] else None
            j_idx = mapping.get(node2) if node2 != nodes[0] else None
            
            # 计算受控源的电流值
            I = 0
            if dep_src.value == "U":
                # 电压控制电流源（VCCS）约束：i_out = k * v_control
                ctrl_node1 = ctrl_branch.node_left
                ctrl_node2 = ctrl_branch.node_right
                
                # 控制节点索引
                ci_idx = mapping.get(ctrl_node1) if ctrl_node1 != nodes[0] else None
                cj_idx = mapping.get(ctrl_node2) if ctrl_node2 != nodes[0] else None
                
                # 更新导纳矩阵
                if ci_idx is not None and i_idx is not None:
                    A[i_idx, ci_idx] -= dep_src.k
                if ci_idx is not None and j_idx is not None:
                    A[j_idx, ci_idx] += dep_src.k
                if cj_idx is not None and i_idx is not None:
                    A[i_idx, cj_idx] += dep_src.k
                if cj_idx is not None and j_idx is not None:
                    A[j_idx, cj_idx] -= dep_src.k
                
            elif dep_src.value == "I":
                # 电流控制电流源（CCCS）约束：i_out = k * i_control
                if i_idx is not None:
                    A[i_idx, ctrl_idx] -= dep_src.k
                if j_idx is not None:
                    A[j_idx, ctrl_idx] += dep_src.k
    
    return A, b, mapping

def solve_circuit(nodes, frequency=1000, solver_method='auto'):
    """
    求解四节点电路（主函数）
    使用修正节点分析法
    
    参数:
        nodes: 节点列表 [node0, node1, node2, node3]
        frequency: 频率，默认1000Hz
        solver_method: 求解方法，可选 'auto', 'direct', 'lstsq', 'pinv'
            - 'auto': 自动选择最佳方法
            - 'direct': 直接求解线性方程组
            - 'lstsq': 最小二乘法求解
            - 'pinv': 使用伪逆求解
        
    返回:
        success: 是否成功求解
        node_voltages: 节点电压字典
        branch_currents: 支路电流字典
    """
    # 检查节点数量
    if len(nodes) != 4:
        print("错误：只支持四节点电路分析")
        return False, None, None
      # 构建和求解MNA矩阵方程
    try:
        A, b, mapping = build_mna_matrix(nodes, frequency)
          # 打印矩阵状态用于调试
        print("MNA矩阵维度:", A.shape)
        print("矩阵条件数:", np.linalg.cond(A))
        print("矩阵行列式:", np.linalg.det(A))
        print("矩阵秩:", np.linalg.matrix_rank(A))
        print("矩阵大小:", A.size)
        print("映射节点:", [node.num for node in mapping.keys() if hasattr(node, 'num')])
        
        # 基于求解方法选择不同的解算方法
        if solver_method == 'direct' or (solver_method == 'auto' and np.linalg.matrix_rank(A) == min(A.shape)):
            # 直接求解方法
            print("使用直接求解方法...")
            x = np.linalg.solve(A, b)
        
        elif solver_method == 'lstsq' or solver_method == 'auto':
            # 最小二乘法
            print("使用最小二乘法求解...")
            x = np.linalg.lstsq(A, b, rcond=None)[0]
            
        elif solver_method == 'pinv':
            # 伪逆法
            print("使用伪逆法求解...")
            x = np.dot(np.linalg.pinv(A), b)
            
    except np.linalg.LinAlgError as e:
        print("错误：矩阵求解失败，电路可能不满足约束条件")
        print(f"详细错误: {str(e)}")
        return False, None, None
    except Exception as e:
        print(f"错误：{str(e)}")
        return False, None, None
    
    # 提取节点电压
    node_voltages = {}
    for node in nodes:
        if node == nodes[0]:  # 参考节点
            node_voltages[node] = 0
        else:
            idx = mapping[node]
            node_voltages[node] = x[idx]
      # 计算支路电流
    branch_currents = {}
    
    # 收集所有受控源，便于后续处理
    dependent_sources = []
    
    # 处理节点间所有支路
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            branches = nodes[i].branches.get(nodes[j], [])
            
            for branch in branches:
                # 电压源支路的电流
                if branch in mapping:
                    idx = mapping[branch]
                    I = x[idx]
                    branch_currents[branch] = I
                    branch.I = I  # 更新支路电流
                # 使用导纳计算其他支路电流
                elif branch.Z != 0:
                    v1 = node_voltages[branch.node_left]
                    v2 = node_voltages[branch.node_right]
                    I = (v1 - v2) * branch.Y
                    branch_currents[branch] = I
                    branch.I = I  # 更新支路电流
                
                # 收集受控源
                for component in branch:
                    if isinstance(component, (DependentVoltageSource, DependentCurrentSource)):
                        dependent_sources.append(component)
    
    # 更新支路电压和元件的电压电流
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            branches = nodes[i].branches.get(nodes[j], [])
            
            for branch in branches:
                # 更新支路电压
                v1 = node_voltages[branch.node_left]
                v2 = node_voltages[branch.node_right]
                branch.V1 = v1
                branch.V2 = v2
                  # 遍历支路上的每个元件，设置电压和电流
                for component in branch:
                    # 设置元件电压
                    component.V1 = v1
                    component.V2 = v2
                    
                    # 只为非受控电压源设置电压值
                    if not isinstance(component, DependentVoltageSource):
                        if component.Vref:
                            component.U = v1 - v2
                        else:
                            component.U = v2 - v1
                    
                    # 设置元件电流
                    if not isinstance(component, (IndependentCurrentSource, DependentCurrentSource)):
                        if component.Iref:
                            component.I = branch.I
                        else:
                            component.I = -branch.I
    
    return True, node_voltages, branch_currents

def print_circuit_solution(nodes, node_voltages, branch_currents):
    """
    以美观易读的方式打印电路求解结果
    
    参数:
        nodes: 节点列表
        node_voltages: 节点电压字典
        branch_currents: 支路电流字典
    """
    from Component import intelligent_output, V_table, V_k, I_table, I_k
    
    print("\n" + "="*50)
    print(" "*15 + "四节点电路仿真结果")
    print("="*50)
    
    # 打印节点电压
    print("\n节点电压：")
    for node, voltage in node_voltages.items():
        if isinstance(voltage, complex):
            mag = abs(voltage)
            phase = math.degrees(math.atan2(voltage.imag, voltage.real))
            v = intelligent_output(mag, V_table, V_k)
            print(f"{node}: {v[0]:.3f}{v[1]} ∠{phase:.2f}°")
        else:
            v = intelligent_output(voltage, V_table, V_k)
            print(f"{node}: {v[0]:.3f}{v[1]}")
    
    # 打印支路电流
    print("\n支路电流：")
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            branches = nodes[i].branches.get(nodes[j], [])
            
            for idx, branch in enumerate(branches):
                current = branch_currents.get(branch)
                if current is None:
                    continue
                
                if isinstance(current, complex):
                    mag = abs(current)
                    phase = math.degrees(math.atan2(current.imag, current.real))
                    i_val = intelligent_output(mag, I_table, I_k)
                    print(f"支路 {nodes[i]}-{nodes[j]} #{idx+1}: {i_val[0]:.3f}{i_val[1]} ∠{phase:.2f}°")
                else:
                    i_val = intelligent_output(current, I_table, I_k)
                    print(f"支路 {nodes[i]}-{nodes[j]} #{idx+1}: {i_val[0]:.3f}{i_val[1]}")
    
    # 打印元件信息
    print("\n元件详情：")
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            branches = nodes[i].branches.get(nodes[j], [])
            
            for branch in branches:
                print(f"\n支路 {branch}:")
                for component in branch:
                    print(f"  {component}")
    
    print("\n" + "="*50)
