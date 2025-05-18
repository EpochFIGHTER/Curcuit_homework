"""
四节点电路简单测试脚本 - 只包含基本元件
"""
import numpy as np
import math
from Core.Component import ElectricalNode, ElectricalBranch, Resistor, Capacitor, Inductor
from Core.Component import IndependentVoltageSource, IndependentCurrentSource
from Core.Component import set_freq
from Core.simulate import solve_circuit, print_circuit_solution

def build_simple_circuit():
    """构建简单测试电路，只包含基本元件"""
    # 设置基础频率为1kHz
    set_freq(1000)
    
    # 构建四个节点
    node0 = ElectricalNode(0)  # 参考节点
    node0.V = 0                # 参考节点电压为0
    node1 = ElectricalNode(1)
    node2 = ElectricalNode(2)
    node3 = ElectricalNode(3)
    nodes = [node0, node1, node2, node3]

    # 支路1: 节点0-1，独立电压源
    branch01 = ElectricalBranch(node0, node1)
    vs1 = IndependentVoltageSource(branch01)
    vs1.U = 10  # 10V电压源
    branch01.append(vs1)

    # 支路2: 节点1-2，电阻
    branch12 = ElectricalBranch(node1, node2)
    r1 = Resistor(branch12)
    r1.R = 1000  # 1kΩ
    branch12.append(r1)

    # 支路3: 节点2-0，电阻
    branch20 = ElectricalBranch(node2, node0)
    r2 = Resistor(branch20)
    r2.R = 2000  # 2kΩ
    branch20.append(r2)

    # 支路4: 节点2-3，电阻
    branch23 = ElectricalBranch(node2, node3)
    r3 = Resistor(branch23)
    r3.R = 3000  # 3kΩ
    branch23.append(r3)

    # 支路5: 节点3-0，电阻
    branch30 = ElectricalBranch(node3, node0)
    r4 = Resistor(branch30)
    r4.R = 4000  # 4kΩ
    branch30.append(r4)

    return nodes

if __name__ == "__main__":
    print("测试简单电阻电压源电路...")
    nodes = build_simple_circuit()
    
    # 尝试不同的求解方法
    solve_methods = ['auto', 'direct', 'lstsq', 'pinv']
    
    for method in solve_methods:
        print(f"\n尝试使用 {method} 方法求解...")
        success, node_voltages, branch_currents = solve_circuit(nodes, solver_method=method)
        
        if success:
            print_circuit_solution(nodes, node_voltages, branch_currents)
            print(f"\n{method} 方法求解成功!")
            break
        else:
            print(f"{method} 方法求解失败")
    
    if not success:
        print("\n所有求解方法均失败，请检查电路结构!")
