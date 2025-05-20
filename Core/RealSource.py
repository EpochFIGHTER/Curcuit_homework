'''
@brief 提供实际电源（有伴电源）的实现，包括有内阻的电压源和有内导的电流源
@detail 实际电压源 = 理想电压源 + 内阻；实际电流源 = 理想电流源 + 内导
'''

import math
if __name__ == "__main__":
    from topology import Node, Branch, Component
    from Component import PowerSource, ElectricalBranch, ElectricalNode, intelligent_output, V_table, V_k, I_table, I_k, R_table, R_k
else:
    from Core.topology import Node, Branch, Component
    from Core.Component import PowerSource, ElectricalBranch, ElectricalNode, intelligent_output, V_table, V_k, I_table, I_k, R_table, R_k

# 全局频率变量，与Component.py保持一致
OMEGA = None  

class RealVoltageSource(PowerSource):
    '''
    @brief 实际电压源类
    @detail 实际电压源 = 理想电压源 + 内阻
    '''
    
    def __init__(self, branch : ElectricalBranch=None, prefix : str = "U"):
        '''
        @brief 实际电压源构造函数
        @param branch 所在支路
        @param prefix 二端元件前缀，默认为U
        '''
        super().__init__(branch, prefix)
        self._internal_resistance = 0.0  # 内阻，默认为0（理想电压源）
        self._emf = 0.0  # 电动势（开路电压）
    
    def _get_internal_resistance(self):
        '''获取内阻值'''
        return self._internal_resistance
        
    def _set_internal_resistance(self, resistance):
        '''设置内阻值'''
        self._internal_resistance = float(resistance)
        
    internal_resistance = property(_get_internal_resistance, _set_internal_resistance)  # 内阻
    
    def _get_emf(self):
        '''获取电动势（开路电压）'''
        return self._emf
        
    def _set_emf(self, emf):
        '''设置电动势'''
        self._emf = float(emf)
        
    emf = property(_get_emf, _set_emf)  # 电动势（开路电压）
    
    @property
    def Z(self):
        '''
        @brief 重写Z属性，返回内阻
        @return 内阻（复数形式）
        '''
        return complex(self._internal_resistance, 0)
    
    @property
    def Y(self):
        '''
        @brief 重写Y属性，返回内导
        @return 内导（复数形式）
        '''
        if self._internal_resistance == 0:
            return None  # 理想电压源导纳为0，在矩阵中特殊处理
        return 1.0 / complex(self._internal_resistance, 0)
    
    def _get_U(self):
        '''
        @brief 获取端电压
        @return 端电压（考虑内阻后的实际输出电压）
        '''
        # 如果电流已知，可以计算端电压：U = E - I*r
        if self.I is not None:
            return self._emf - self.I * self._internal_resistance
        return self._emf  # 如果电流未知，返回电动势
    
    def _set_U(self, U):
        '''
        @brief 设置端电压（仅用于显示）
        '''
        # 实际电压源的端电压是由电动势和内阻计算得出的，不能直接设置
        # 此方法目前仅用于兼容接口，不建议使用
        pass
    
    U = property(_get_U, _set_U)  # 端电压
    
    def __str__(self):
        '''
        @brief 重写字符串表示
        @return 实际电压源的字符串表示
        '''
        emf_str = intelligent_output(self._emf, V_table, V_k)
        r_str = intelligent_output(self._internal_resistance, R_table, R_k)
        
        if self.I is not None:
            u_str = intelligent_output(self.U, V_table, V_k)
            i_str = intelligent_output(self.I, I_table, I_k)
            return f"{self.prefix}{self.num} E={emf_str[0]:.2f}{emf_str[1]}, r={r_str[0]:.2f}{r_str[1]}, U={u_str[0]:.2f}{u_str[1]}, I={i_str[0]:.2f}{i_str[1]}"
        else:
            return f"{self.prefix}{self.num} E={emf_str[0]:.2f}{emf_str[1]}, r={r_str[0]:.2f}{r_str[1]}"


class RealCurrentSource(PowerSource):
    '''
    @brief 实际电流源类
    @detail 实际电流源 = 理想电流源 + 内导（并联电阻）
    '''
    
    def __init__(self, branch : ElectricalBranch=None, prefix : str = "I"):
        '''
        @brief 实际电流源构造函数
        @param branch 所在支路
        @param prefix 二端元件前缀，默认为I
        '''
        super().__init__(branch, prefix)
        self._internal_conductance = 0.0  # 内导，默认为0（理想电流源）
        self._ideal_current = 0.0  # 理想电流值
    
    def _get_internal_conductance(self):
        '''获取内导值'''
        return self._internal_conductance
        
    def _set_internal_conductance(self, conductance):
        '''设置内导值'''
        self._internal_conductance = float(conductance)
        
    internal_conductance = property(_get_internal_conductance, _set_internal_conductance)  # 内导
    
    def _get_internal_resistance(self):
        '''获取内阻值(内导的倒数)'''
        if self._internal_conductance == 0:
            return float('inf')  # 理想电流源内阻为无穷大
        return 1.0 / self._internal_conductance
        
    def _set_internal_resistance(self, resistance):
        '''设置内阻值'''
        if resistance == 0:
            self._internal_conductance = float('inf')
        else:
            self._internal_conductance = 1.0 / float(resistance)
        
    internal_resistance = property(_get_internal_resistance, _set_internal_resistance)  # 内阻
    
    def _get_ideal_current(self):
        '''获取理想电流值'''
        return self._ideal_current
        
    def _set_ideal_current(self, current):
        '''设置理想电流值'''
        self._ideal_current = float(current)
        
    ideal_current = property(_get_ideal_current, _set_ideal_current)  # 理想电流值
    
    @property
    def Z(self):
        '''
        @brief 重写Z属性，返回内阻
        @return 内阻（复数形式）
        '''
        if self._internal_conductance == 0:
            return complex(float('inf'), 0)  # 理想电流源阻抗为无穷大
        return complex(1.0 / self._internal_conductance, 0)
    
    @property
    def Y(self):
        '''
        @brief 重写Y属性，返回内导
        @return 内导（复数形式）
        '''
        return complex(self._internal_conductance, 0)
    
    def _get_I(self):
        '''
        @brief 获取输出电流
        @return 输出电流（考虑内导后的实际输出电流）
        '''
        # 如果电压已知，可以计算输出电流：I = I_ideal - U*G
        if self.U is not None and self._internal_conductance > 0:
            return self._ideal_current - self.U * self._internal_conductance
        return self._ideal_current  # 如果电压未知或内导为0，返回理想电流
    
    def _set_I(self, I):
        '''
        @brief 设置输出电流（仅用于显示）
        '''
        # 实际电流源的输出电流是由理想电流和内导计算得出的，不能直接设置
        # 此方法目前仅用于兼容接口，不建议使用
        pass
    
    I = property(_get_I, _set_I)  # 输出电流
    
    def __str__(self):
        '''
        @brief 重写字符串表示
        @return 实际电流源的字符串表示
        '''
        ideal_i_str = intelligent_output(self._ideal_current, I_table, I_k)
        
        if self._internal_conductance > 0:
            r_str = intelligent_output(1.0 / self._internal_conductance, R_table, R_k)
            return f"{self.prefix}{self.num} I_ideal={ideal_i_str[0]:.2f}{ideal_i_str[1]}, R_p={r_str[0]:.2f}{r_str[1]}"
        else:
            return f"{self.prefix}{self.num} I_ideal={ideal_i_str[0]:.2f}{ideal_i_str[1]}, R_p=∞"


# 下面是测试用代码
if __name__ == "__main__":
    # 简单的测试
    node0 = ElectricalNode(0)
    node1 = ElectricalNode(1)
    
    branch = ElectricalBranch(node0, node1)
    
    # 测试有内阻的电压源
    real_vs = RealVoltageSource(branch)
    real_vs.emf = 10.0  # 10V电动势
    real_vs.internal_resistance = 2.0  # 2Ω内阻
    real_vs.I = 1.0  # 设置1A电流，用于测试
    
    print("=== 有内阻的电压源测试 ===")
    print(f"电动势: {real_vs.emf}V")
    print(f"内阻: {real_vs.internal_resistance}Ω")
    print(f"电流: {real_vs.I}A")
    print(f"端电压: {real_vs.U}V")  # 应该为 10V - 1A * 2Ω = 8V
    print(f"阻抗: {real_vs.Z}Ω")
    print(real_vs)
    
    print("\n=== 有内导的电流源测试 ===")
    real_cs = RealCurrentSource(branch)
    real_cs.ideal_current = 0.5  # 0.5A理想电流
    real_cs.internal_resistance = 10.0  # 10Ω内阻(并联)
    real_cs.U = 2.0  # 设置2V电压，用于测试
    
    print(f"理想电流: {real_cs.ideal_current}A")
    print(f"内阻: {real_cs.internal_resistance}Ω")
    print(f"内导: {real_cs.internal_conductance}S")
    print(f"电压: {real_cs.U}V")
    print(f"输出电流: {real_cs.I}A")  # 应该为 0.5A - 2V * 0.1S = 0.3A
    print(real_cs)
