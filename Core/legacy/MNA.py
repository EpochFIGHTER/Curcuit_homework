'''
@brief 修正节点分析(MNA)方法的实现，支持含内阻的电压源和各种元件
@detail 基于节点电压法(nodal analysis)的扩展，能处理有伴电源和理想电源
'''

import numpy as np  # type: ignore
import math

if __name__ == "__main__":
    from Component import ElectricalNode, IndependentVoltageSource, IndependentCurrentSource, Resistor
    from RealSource import RealVoltageSource, RealCurrentSource
    # from Dependent import VoltageControlledVoltageSource, CurrentControlledVoltageSource  # 如果有的话
    from Component import ElectricalBranch
else:
    from Core.Component import ElectricalNode, IndependentVoltageSource, IndependentCurrentSource, ElectricalBranch, Resistor
    from Core.RealSource import RealVoltageSource, RealCurrentSource
    try:
        from Core.DependentSource import VoltageControlledVoltageSource, CurrentControlledVoltageSource
    except ImportError:
        pass  # 如果没有受控源模块，跳过导入

# 全局频率变量
OMEGA = None

def set_frequency(freq):
    '''
    @brief 设置分析频率
    @param freq 频率(Hz)
    '''
    global OMEGA
    OMEGA = 2 * math.pi * freq


def build_mna(nodes, reference_node=None, frequency=1000):
    '''
    @brief 构建修正节点分析(MNA)方程，支持有内阻的电压源和其它元件
    @param nodes 所有节点列表
    @param reference_node 参考节点(接地点)
    @param frequency 分析频率(Hz)
    @return (A, b, x_map) 系数矩阵、常数向量、变量映射
    '''
    # 设置分析频率
    set_frequency(frequency)
    
    # 1. 选择参考节点
    if reference_node is None:
        reference_node = nodes[0]  # 默认选第一个节点为参考点
    
    # 2. 找出所有非参考节点、理想电压源和电流源支路
    independent_nodes = [node for node in nodes if node != reference_node]
    ideal_voltage_sources = []
    current_source_branches = []  # 记录含有电流源的支路
    
    # 搜集电路中的所有理想电压源(内阻为0)和电流源支路
    for node in nodes:
        for neighbor in node.branches:
            for branch in node.branches[neighbor]:
                has_current_source = False
                
                # 先检查支路上是否有电流源
                for component in branch:
                    if isinstance(component, IndependentCurrentSource) or \
                       isinstance(component, RealCurrentSource):
                        has_current_source = True
                        if branch not in current_source_branches:
                            current_source_branches.append(branch)
                        break
                
                # 如果支路上没有电流源，再检查是否有理想电压源
                if not has_current_source:
                    for component in branch:
                        # 检查是否为理想电压源(独立或受控)
                        if isinstance(component, IndependentVoltageSource) or \
                           (isinstance(component, RealVoltageSource) and component.internal_resistance == 0) or \
                           (hasattr(component, '__class__') and component.__class__.__name__ in 
                            ['VoltageControlledVoltageSource', 'CurrentControlledVoltageSource']):
                            if component not in ideal_voltage_sources:
                                ideal_voltage_sources.append(component)
    
    # 3. 确定方程规模
    n = len(independent_nodes)  # 非参考节点数量
    m = len(ideal_voltage_sources)  # 理想电压源数量
    size = n + m  # 总方程数
    
    # 4. 初始化方程组
    A = np.zeros((size, size), dtype=complex)
    b = np.zeros(size, dtype=complex)
    
    # 5. 构建变量映射
    x_map = {}
    for i, node in enumerate(independent_nodes):
        x_map[f"V_{node.num}"] = i  # 节点电压变量
    
    for i, vs in enumerate(ideal_voltage_sources):
        if hasattr(vs, 'prefix') and hasattr(vs, 'num'):
            x_map[f"I_{vs.prefix}{vs.num}"] = n + i  # 电压源电流变量
        else:
            x_map[f"I_{vs}"] = n + i  # 未命名电压源
    
    # 6. 填充导纳矩阵部分(节点方程)
    for i, node_i in enumerate(independent_nodes):
        for j, node_j in enumerate(independent_nodes):
            if i == j:  # 自导纳
                # 所有与节点i相连的支路的导纳之和
                for neighbor in node_i.branches:
                    for branch in node_i.branches[neighbor]:
                        # 跳过含有电流源和理想电压源的支路
                        if branch in current_source_branches:
                            continue
                            
                        # 遍历支路上所有元件
                        for component in branch:
                            # 跳过理想电压源
                            if component in ideal_voltage_sources:
                                continue
                            
                            # 使用元件的导纳
                            if hasattr(component, 'Y') and component.Y is not None:
                                A[i, i] += component.Y
            
            else:  # 互导纳
                # 节点i和j之间的导纳(取负值)
                if node_j in node_i.branches:
                    for branch in node_i.branches[node_j]:
                        # 跳过含有电流源的支路
                        if branch in current_source_branches:
                            continue
                            
                        # 遍历支路上所有元件
                        for component in branch:
                            # 跳过理想电压源
                            if component in ideal_voltage_sources:
                                continue
                            
                            # 使用元件的导纳
                            if hasattr(component, 'Y') and component.Y is not None:
                                A[i, j] -= component.Y
    
    # 7. 处理电流源支路的贡献
    for branch in current_source_branches:
        # 找到该支路上的电流源
        current_source = None
        for component in branch:
            if isinstance(component, IndependentCurrentSource) or \
               isinstance(component, RealCurrentSource):
                current_source = component
                break
        
        if current_source is None:
            continue
            
        # 获取支路连接的节点
        node_left = branch.node_left
        node_right = branch.node_right
        
        # 计算电流值
        current_value = 0
        if isinstance(current_source, IndependentCurrentSource):
            current_value = current_source.ideal_current if hasattr(current_source, 'ideal_current') else current_source.I
        elif isinstance(current_source, RealCurrentSource):
            current_value = current_source.ideal_current
        
        # 处理电流源的内导（并联电阻）
        # 如果是RealCurrentSource，将内导部分加入导纳矩阵
        if isinstance(current_source, RealCurrentSource) and current_source.internal_conductance > 0:
            # 获取节点在方程中的索引
            left_index = independent_nodes.index(node_left) if node_left != reference_node and node_left in independent_nodes else None
            right_index = independent_nodes.index(node_right) if node_right != reference_node and node_right in independent_nodes else None
            
            # 将内导部分添加到导纳矩阵
            if left_index is not None and right_index is not None:
                # 只处理节点方程
                A[left_index, left_index] += current_source.internal_conductance
                A[right_index, right_index] += current_source.internal_conductance
                A[left_index, right_index] -= current_source.internal_conductance
                A[right_index, left_index] -= current_source.internal_conductance
            elif left_index is not None:
                A[left_index, left_index] += current_source.internal_conductance
            elif right_index is not None:
                A[right_index, right_index] += current_source.internal_conductance
         
        # 将电流分配到节点方程
        if node_left != reference_node and node_left in independent_nodes:
            i = independent_nodes.index(node_left)
            # 如果电流从左端流出，对应方程右侧增加正的电流项
            sign_left = -1 if current_source.Iref else 1
            b[i] += sign_left * current_value
            
        if node_right != reference_node and node_right in independent_nodes:
            i = independent_nodes.index(node_right)
            # 如果电流从右端流入，对应方程右侧增加负的电流项
            sign_right = 1 if current_source.Iref else -1
            b[i] += sign_right * current_value
            
        # 将电流值设置给电流源，便于后续处理
        current_source.I = current_value
    
    # 8. 处理理想电压源
    for k, vs in enumerate(ideal_voltage_sources):
        eq_idx = n + k  # 电压源方程索引
        
        # 找出电压源连接的两个节点
        node1, node2 = None, None
        for node in nodes:
            for neighbor in node.branches:
                for branch in node.branches[neighbor]:
                    if vs in branch:
                        # 确定电压源的正负极
                        if vs.Vref:  # 左端为正
                            node1 = branch.node_left
                            node2 = branch.node_right
                        else:  # 右端为正
                            node1 = branch.node_right
                            node2 = branch.node_left
                        break
        
        if node1 is None or node2 is None:
            continue  # 如果找不到连接节点，跳过此电压源
        
        # 节点电压方程中加入电压源电流
        if node1 != reference_node:
            node1_idx = independent_nodes.index(node1)
            A[node1_idx, eq_idx] += 1  # 电流从节点1流出
        
        if node2 != reference_node:
            node2_idx = independent_nodes.index(node2)
            A[node2_idx, eq_idx] -= 1  # 电流流向节点2
        
        # 电压源方程: V1 - V2 = Vs
        if node1 != reference_node:
            node1_idx = independent_nodes.index(node1)
            A[eq_idx, node1_idx] += 1  # V1项
        
        if node2 != reference_node:
            node2_idx = independent_nodes.index(node2)
            A[eq_idx, node2_idx] -= 1  # V2项
        
        # 处理不同类型的电压源
        if isinstance(vs, IndependentVoltageSource):
            b[eq_idx] = vs.U  # 独立电压源
            
        elif isinstance(vs, RealVoltageSource):
            b[eq_idx] = vs.emf  # 有伴电压源，使用电动势
            
        # 可以扩展处理受控电压源
        elif hasattr(vs, '__class__') and vs.__class__.__name__ == 'VoltageControlledVoltageSource':
            # 电压控制电压源
            pos_node, neg_node = vs.control_nodes
            
            if pos_node != reference_node:
                pos_idx = independent_nodes.index(pos_node)
                A[eq_idx, pos_idx] -= vs.control_value  # -μVc+
            
            if neg_node != reference_node:
                neg_idx = independent_nodes.index(neg_node)
                A[eq_idx, neg_idx] += vs.control_value  # +μVc-
    
    return A, b, x_map


def solve_circuit(nodes, reference_node=None, frequency=1000):
    '''
    @brief 求解整个电路
    @param nodes 所有节点列表
    @param reference_node 参考节点
    @param frequency 分析频率(Hz)
    @return 解字典，包含所有节点电压和电压源电流
    '''
    # 1. 构建MNA方程
    A, b, x_map = build_mna(nodes, reference_node, frequency)
    
    try:
        # 2. 求解方程组
        x = np.linalg.solve(A, b)
        
        # 3. 整理解
        solution = {}
        for var_name, idx in x_map.items():
            solution[var_name] = x[idx]
        
        # 4. 设置节点电压
        if reference_node:
            reference_node.V = 0  # 参考节点电压为0
        
        for i, node in enumerate(node for node in nodes if node != reference_node):
            if f"V_{node.num}" in solution:
                node.V = solution[f"V_{node.num}"]
        
        # 5. 计算支路电流和元件电压
        # 收集电流源支路和理想电压源支路
        current_source_branches = []
        ideal_voltage_source_branches = []
        for node in nodes:
            for neighbor in node.branches:
                for branch in node.branches[neighbor]:
                    has_current_source = False
                    has_ideal_vs = False
                    
                    # 检查支路上是否有电流源
                    for component in branch:
                        if isinstance(component, IndependentCurrentSource) or \
                           isinstance(component, RealCurrentSource):
                            has_current_source = True
                            if branch not in current_source_branches:
                                current_source_branches.append(branch)
                            break
                    
                    # 检查是否有理想电压源
                    for component in branch:
                        if (isinstance(component, IndependentVoltageSource) and getattr(component, 'internal_resistance', 0) == 0) or \
                           (isinstance(component, RealVoltageSource) and component.internal_resistance == 0) or \
                           (hasattr(component, '__class__') and component.__class__.__name__ in 
                            ['VoltageControlledVoltageSource', 'CurrentControlledVoltageSource']):
                            has_ideal_vs = True
                            if branch not in ideal_voltage_source_branches:
                                ideal_voltage_source_branches.append(branch)
                            # 设置电压源电流
                            if hasattr(component, 'prefix') and hasattr(component, 'num'):
                                key = f"I_{component.prefix}{component.num}"
                                if key in solution:
                                    component.I = solution[key]
                            break
        
        # 处理普通支路
        for node in nodes:
            for neighbor in node.branches:
                for branch in node.branches[neighbor]:
                    # 跳过电流源和理想电压源支路，它们有特殊处理
                    if branch in current_source_branches or branch in ideal_voltage_source_branches:
                        continue
                    
                    # 对于普通支路，计算电流
                    if hasattr(branch, 'Z') and branch.Z != 0:
                        # 计算支路电流
                        v_diff = node.V - neighbor.V
                        branch.I = v_diff / branch.Z
                        
                        # 设置支路上所有元件的电流
                        for component in branch:
                            component.I = branch.I
        
        # 处理电流源支路
        for branch in current_source_branches:
            current_source = None
            for component in branch:
                if isinstance(component, IndependentCurrentSource) or \
                   isinstance(component, RealCurrentSource):
                    current_source = component
                    break
            
            if current_source is None:
                continue
                
            # 获取电流源的电流值
            branch_current = 0
            if isinstance(current_source, IndependentCurrentSource):
                branch_current = current_source.ideal_current if hasattr(current_source, 'ideal_current') else current_source.I
            elif isinstance(current_source, RealCurrentSource):
                branch_current = current_source.ideal_current
                
                # 如果有内导，考虑电压影响
                if current_source.internal_conductance > 0:
                    # 计算两端的电压差
                    v_diff = branch.node_left.V - branch.node_right.V
                    if not current_source.Vref:
                        v_diff = -v_diff
                    current_source.U = abs(v_diff)  # 设置电流源电压
                    # 计算实际电流 = 理想电流 - 内导 * 电压
                    branch_current = current_source.ideal_current - current_source.internal_conductance * v_diff
            
            # 设置支路电流
            branch.I = branch_current
            
            # 设置支路上所有元件的电流
            for component in branch:
                component.I = branch_current
            
        # 设置所有元件的端电压
        for node in nodes:
            for neighbor in node.branches:
                for branch in node.branches[neighbor]:
                    for component in branch:
                        if hasattr(component, 'V1') and hasattr(component, 'V2'):
                            if component.Vref:  # 左端为正
                                component.V1 = branch.node_left.V
                                component.V2 = branch.node_right.V
                            else:  # 右端为正
                                component.V1 = branch.node_right.V
                                component.V2 = branch.node_left.V
                        
                        # 计算压降
                        if hasattr(component, 'U') and hasattr(component, 'V1') and hasattr(component, 'V2'):
                            component.U = abs(component.V1 - component.V2)
        
        return solution
        
    except np.linalg.LinAlgError:
        print("错误: 矩阵不可逆，电路可能存在问题")
        return None


# 下面是测试用代码
if __name__ == "__main__":
    # 简单的电路测试：内阻电压源 + 电阻负载
    print("=== 有内阻电压源测试 ===")
    
    n0 = ElectricalNode(0)  # 接地点
    n1 = ElectricalNode(1)  # 负载连接点
    
    branch = n0.connect_to(n1, ElectricalBranch)
    
    # 创建有内阻的电压源和负载电阻
    vs = RealVoltageSource(branch)
    vs.emf = 10.0  # 10V电动势
    vs.internal_resistance = 2.0  # 2Ω内阻
    
    # 尝试解算
    solution = solve_circuit([n0, n1], n0)
    
    if solution:
        print(f"节点0电压: {n0.V:.2f} V (接地点)")
        print(f"节点1电压: {n1.V:.2f} V")
        print(f"电压源电流: {vs.I:.2f} A")
        print(f"电压源端电压: {vs.U:.2f} V")
        
    print("\n=== 完整电路测试 ===")
    # 创建四节点电路
    n0 = ElectricalNode(0)  # 接地点
    n1 = ElectricalNode(1)
    n2 = ElectricalNode(2)
    n3 = ElectricalNode(3)
    
    # 创建支路
    b01 = n0.connect_to(n1, ElectricalBranch)
    b12 = n1.connect_to(n2, ElectricalBranch)
    b23 = n2.connect_to(n3, ElectricalBranch)
    b30 = n3.connect_to(n0, ElectricalBranch)
    
    # 添加元件
    vs = RealVoltageSource(b01)
    vs.emf = 12.0  # 12V电动势
    vs.internal_resistance = 0.5  # 0.5Ω内阻
    
    # 解算电路
    solution = solve_circuit([n0, n1, n2, n3], n0)
    
    if solution:
        print(f"节点0电压: {n0.V:.2f} V (接地点)")
        print(f"节点1电压: {n1.V:.2f} V")
        print(f"节点2电压: {n2.V:.2f} V")
        print(f"节点3电压: {n3.V:.2f} V")
        print(f"电压源电流: {vs.I:.2f} A")
        print(f"电压源端电压: {vs.U:.2f} V")
    
    print("\n=== 电流源测试 ===")
    # 创建简单的电流源电路：电流源 + 电阻串联
    n0 = ElectricalNode(0)  # 接地点
    n1 = ElectricalNode(1)  # 连接点
    
    # 创建支路
    branch = n0.connect_to(n1, ElectricalBranch)
    
    # 创建有内导的电流源
    cs = RealCurrentSource(branch)
    cs.ideal_current = 0.5  # 0.5A理想电流
    cs.internal_resistance = 1000.0  # 1000Ω内阻(并联)
    
    # 解算电路
    solution = solve_circuit([n0, n1], n0)
    
    if solution:
        print(f"节点0电压: {n0.V:.2f} V (接地点)")
        print(f"节点1电压: {n1.V:.2f} V")
        print(f"电流源电流: {cs.I:.2f} A")
        print(f"电流源端电压: {cs.U:.2f} V")
        
    print("\n=== 电流源串联元件测试 ===")
    # 创建电流源串联电阻的电路
    n0 = ElectricalNode(0)  # 接地点
    n1 = ElectricalNode(1)  # 中间节点
    n2 = ElectricalNode(2)  # 终端节点
    
    # 创建支路
    b01 = n0.connect_to(n1, ElectricalBranch)
    b12 = n1.connect_to(n2, ElectricalBranch)
    
    # 在b01支路上添加电流源
    cs = RealCurrentSource(b01)
    cs.ideal_current = 0.5  # 0.5A理想电流
    cs.internal_resistance = 100.0  # 100Ω内阻(并联)
    
    # 在b12支路上添加电阻
    resistor = Resistor(b12)
    resistor.R = 10.0  # 10Ω电阻
    
    # 解算电路
    solution = solve_circuit([n0, n1, n2], n0)
    
    if solution:
        print(f"节点0电压: {n0.V:.2f} V (接地点)")
        print(f"节点1电压: {n1.V:.2f} V")
        print(f"节点2电压: {n2.V:.2f} V")
        print(f"电流源电流: {cs.I:.2f} A")
        print(f"电流源端电压: {cs.U:.2f} V")
        print(f"电阻电流: {resistor.I:.2f} A")
        print(f"电阻压降: {resistor.U:.2f} V")
