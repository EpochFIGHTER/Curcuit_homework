"""
四节点电路仿真测试脚本
包含独立源、受控源、RLC元件、并联、串联等典型情况
"""
import numpy as np
import math
from Core.Component import ElectricalNode, ElectricalBranch, Resistor, Capacitor, Inductor
from Core.Component import IndependentVoltageSource, IndependentCurrentSource, DependentVoltageSource, DependentCurrentSource
from Core.Component import set_freq
from Core.simulate import solve_circuit, print_circuit_solution

def build_test_circuit():
    """构建测试电路，包含各种类型元件和连接方式"""
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

    # 支路6: 节点1-3，受控电压源（由支路1-2的电阻r1的电压控制）
    branch13 = ElectricalBranch(node1, node3)
    dvs = DependentVoltageSource(branch13)
    dvs.controler = r1  # 受r1电压控制
    dvs.value = "U"     # 控制量为电压
    dvs.k = 2           # 增益为2
    branch13.append(dvs)

    # 支路7: 节点0-2与支路2-0并联，独立电流源
    branch02 = ElectricalBranch(node0, node2)
    is1 = IndependentCurrentSource(branch02)
    is1.I = 0.005  # 5mA
    branch02.append(is1)

    # 支路8: 节点0-3与支路3-0并联，受控电流源（由支路0-1的电压源控制）
    branch03 = ElectricalBranch(node0, node3)
    dcs = DependentCurrentSource(branch03)
    dcs.controler = vs1  # 受vs1电压控制
    dcs.value = "U"      # 控制量为电压
    dcs.k = 0.001        # 增益为0.001 (1mA/V)
    branch03.append(dcs)

    return nodes

def test_with_different_frequencies():
    """测试不同频率下的电路响应"""
    frequencies = [100, 1000, 10000]  # 100Hz, 1kHz, 10kHz
    
    nodes = build_test_circuit()
    
    for freq in frequencies:
        print(f"\n\n测试频率: {freq}Hz")
        success, node_voltages, branch_currents = solve_circuit(nodes, freq)
        
        if success:
            print_circuit_solution(nodes, node_voltages, branch_currents)
        else:
            print(f"频率 {freq}Hz 的求解失败")

def test_circuit_with_varying_components():
    """测试不同元件值对电路的影响"""
    # 基础测试电路
    nodes = build_test_circuit()
    
    # 测试基础电路
    print("\n基础电路测试:")
    success, node_voltages, branch_currents = solve_circuit(nodes)
    if success:
        print_circuit_solution(nodes, node_voltages, branch_currents)
    
    # 修改元件值并重新测试
    # 这里可以添加更多元件值变化的测试...

if __name__ == "__main__":
    print("测试完整电路（含受控源）...")
    nodes = build_test_circuit()
    
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
    
    # 可选: 取消注释以测试不同频率
    # test_with_different_frequencies()
