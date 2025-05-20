'''
@brief 提供有伴电源的实现，包括电压控制电压源(VCVS)和电流控制电压源(CCVS)
'''

import math
if __name__ == "__main__":
    from topology import Node, Branch, Component
    from Component import PowerSource, ElectricalBranch, ElectricalNode, intelligent_output, V_table, V_k
else:
    from Core.topology import Node, Branch, Component
    from Core.Component import PowerSource, ElectricalBranch, ElectricalNode, intelligent_output, V_table, V_k

# 全局频率变量，与Component.py保持一致
OMEGA = None  

class DependentVoltageSource(PowerSource):
    '''
    @brief 有伴电压源基类
    @detail 有伴电压源的导纳不能简单表示，需要修正节点分析法处理
    '''
    
    def __init__(self, branch : ElectricalBranch=None, prefix : str = "E"):
        '''
        @brief 有伴电压源基类构造函数
        @param branch 所在支路
        @param prefix 二端元件前缀，默认为E
        '''
        super().__init__(branch, prefix)
        self.control_value = 0  # 控制参数(增益)
    
    @property
    def Y(self):
        # 有伴电压源不能用导纳表示，需要MNA方法特殊处理
        return None
    
    def __str__(self):
        if hasattr(self, 'U') and self.U is not None:
            u = intelligent_output(self.U, V_table, V_k)
            return f"{self.prefix}{self.num} U={u[0]:.2f}{u[1]}"
        else:
            return f"{self.prefix}{self.num}"


class VoltageControlledVoltageSource(DependentVoltageSource):
    '''
    @brief 电压控制电压源(VCVS)
    @detail 输出电压与控制节点之间的电压成正比
    '''
    
    def __init__(self, branch : ElectricalBranch=None, prefix : str = "E"):
        '''
        @brief 电压控制电压源构造函数
        @param branch 所在支路
        @param prefix 二端元件前缀，默认为E
        '''
        super().__init__(branch, prefix)
        self.control_nodes = (None, None)  # 控制节点对(正端, 负端)
    
    def set_control(self, positive_node : ElectricalNode, negative_node : ElectricalNode, gain : float):
        '''
        @brief 设置控制参数
        @param positive_node 控制电压正端节点
        @param negative_node 控制电压负端节点
        @param gain 电压增益
        '''
        self.control_nodes = (positive_node, negative_node)
        self.control_value = gain
    
    def _get_U(self):
        # 如果控制节点电压已知，可以计算输出电压
        pos, neg = self.control_nodes
        if pos is not None and neg is not None and pos.V is not None and neg.V is not None:
            return self.control_value * (pos.V - neg.V)
        return None
    
    U = property(_get_U)  # 电压，只读
    
    def __str__(self):
        if self.control_nodes[0] is not None:
            return f"{self.prefix}{self.num} μ={self.control_value:.2f}, 控制节点=({self.control_nodes[0]}, {self.control_nodes[1]})"
        else:
            return f"{self.prefix}{self.num}"


class CurrentControlledVoltageSource(DependentVoltageSource):
    '''
    @brief 电流控制电压源(CCVS)
    @detail 输出电压与控制支路的电流成正比
    '''
    
    def __init__(self, branch : ElectricalBranch=None, prefix : str = "H"):
        '''
        @brief 电流控制电压源构造函数
        @param branch 所在支路
        @param prefix 二端元件前缀，默认为H
        '''
        super().__init__(branch, prefix)
        self.control_branch = None  # 控制支路
    
    def set_control(self, control_branch : ElectricalBranch, transresistance : float):
        '''
        @brief 设置控制参数
        @param control_branch 控制电流所在支路
        @param transresistance 跨阻增益(单位:Ω)
        '''
        self.control_branch = control_branch
        self.control_value = transresistance
    
    def _get_U(self):
        # 如果控制支路电流已知，可以计算输出电压
        if self.control_branch is not None and self.control_branch.I is not None:
            return self.control_value * self.control_branch.I
        return None
    
    U = property(_get_U)  # 电压，只读
    
    def __str__(self):
        if self.control_branch is not None:
            return f"{self.prefix}{self.num} r={self.control_value:.2f}Ω, 控制支路={self.control_branch}"
        else:
            return f"{self.prefix}{self.num}"


# 下面是测试用代码
if __name__ == "__main__":
    # 简单的测试
    node0 = ElectricalNode(0)
    node1 = ElectricalNode(1)
    node2 = ElectricalNode(2)
    
    branch1 = ElectricalBranch(node0, node1)
    branch2 = ElectricalBranch(node1, node2)
    
    vcvs = VoltageControlledVoltageSource(branch2)
    vcvs.set_control(node0, node1, 2.5)
    
    # 设置控制电压
    node0.V = 0
    node1.V = 1.0
    
    print(f"控制电压: {node0.V - node1.V}V")
    print(f"VCVS输出: {vcvs.U}V")
    print(vcvs)
