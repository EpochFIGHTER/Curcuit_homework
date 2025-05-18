"""
四节点电路仿真测试脚本 - 简化版（不含受控源）
"""
import numpy as np
import math
from Core.Component import ElectricalNode, ElectricalBranch, Resistor, Capacitor, Inductor
from Core.Component import IndependentVoltageSource, IndependentCurrentSource
from Core.Component import set_freq
from Core.simulate import solve_circuit, print_circuit_solution

def build_simple_test_circuit():
    """构建不含受控源的测试电路"""
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

    # 支路4: 节点2-3，电容
    branch23 = ElectricalBranch(node2, node3)
    c1 = Capacitor(branch23)
    c1.C = 1e-6  # 1μF
    branch23.append(c1)

    # 支路5: 节点3-0，电感
    branch30 = ElectricalBranch(node3, node0)
    l1 = Inductor(branch30)
    l1.L = 0.01  # 10mH
    branch30.append(l1)

    # 支路6: 节点1-3，电阻
    branch13 = ElectricalBranch(node1, node3)
    r3 = Resistor(branch13)
    r3.R = 5000  # 5kΩ
    branch13.append(r3)

    # 支路7: 节点0-2与支路2-0并联，独立电流源
    branch02 = ElectricalBranch(node0, node2)
    is1 = IndependentCurrentSource(branch02)
    is1.I = 0.005  # 5mA
    branch02.append(is1)

    return nodes

if __name__ == "__main__":
    print("测试简化电路（不含受控源）...")
    nodes = build_simple_test_circuit()
    
    # 尝试不同的求解方法
    solve_methods = ['auto', 'lstsq', 'pinv', 'direct']
    
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
