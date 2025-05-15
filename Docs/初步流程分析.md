---
### **一、问题拆解**
我们需要处理一个**4结点电路（含参考地）**，其中3个为独立结点，结点间可能存在：
1. **多种支路类型**：电阻（R）、电感（L）、电容（C）、独立电压源（V）、独立电流源（I）、受控源
2. **多支路并联**：如结点1-2间同时存在电阻和电压源
3. **不同接地情况**：参考结点（通常为地）可能连接任意元件
---

### **二、伪代码分场景实现**

#### **1. 基础数据结构**

```python
circuit = {
    "nodes": ["N1", "N2", "N3", "0"],  # 0为参考地
    "branches": [
        {"type": "R", "from": "N1", "to": "N2", "value": 10},
        {"type": "V", "from": "N1", "to": "0", "value": 5},
        {"type": "C", "from": "N2", "to": "N3", "value": 1e-6},
        {"type": "I", "from": "N3", "to": "0", "value": 2}
    ],
    "omega": 1000  # 正弦稳态角频率(rad/s)
}
```

#### **2. 场景 1：纯电阻网络**

```python
def build_resistive_matrix(circuit):
    n = len(circuit["nodes"]) - 1  # 忽略参考地
    Y = [[0 for _ in range(n)] for _ in range(n)]
    for branch in circuit["branches"]:
        if branch["type"] != "R":
            continue
        i = circuit["nodes"].index(branch["from"]) - 1  # 排除参考地
        j = circuit["nodes"].index(branch["to"]) - 1
        g = 1 / branch["value"]  # 电导
        if i >= 0: Y[i][i] += g
        if j >= 0: Y[j][j] += g
        if i >=0 and j >=0:
            Y[i][j] -= g
            Y[j][i] -= g
    return Y
```

#### **3. 场景 2：含动态元件（L/C）**

```python
def build_complex_matrix(circuit):
    n = len(circuit["nodes"]) - 1
    Y = [[0+0j for _ in range(n)] for _ in range(n)]
    for branch in circuit["branches"]:
        i = circuit["nodes"].index(branch["from"]) - 1
        j = circuit["nodes"].index(branch["to"]) - 1
        if branch["type"] == "R":
            y = 1 / branch["value"]
        elif branch["type"] == "L":
            y = 1 / (1j * circuit["omega"] * branch["value"])
        elif branch["type"] == "C":
            y = 1j * circuit["omega"] * branch["value"]
        else:
            continue  # 电源后续处理
        # 更新矩阵（同电阻逻辑）
        if i >= 0: Y[i][i] += y
        if j >= 0: Y[j][j] += y
        if i >=0 and j >=0:
            Y[i][j] -= y
            Y[j][i] -= y
    return Y
```

#### **4. 场景 3：处理独立电源**

```python
def add_sources(Y, I, circuit):
    n = len(circuit["nodes"]) - 1
    for branch in circuit["branches"]:
        if branch["type"] == "V":  # 电压源→超级结点
            i = circuit["nodes"].index(branch["from"]) - 1
            j = circuit["nodes"].index(branch["to"]) - 1
            if i >=0 and j >=0:  # 非接地电压源
                Y[i][i] += 1e9; Y[j][j] += 1e9  # 大数法
                Y[i][j] -= 1e9; Y[j][i] -= 1e9
                I[i] += branch["value"] * 1e9
                I[j] -= branch["value"] * 1e9
        elif branch["type"] == "I":  # 电流源→直接注入
            i = circuit["nodes"].index(branch["from"]) - 1
            j = circuit["nodes"].index(branch["to"]) - 1
            if i >=0: I[i] -= branch["value"]  # 流出为负
            if j >=0: I[j] += branch["value"]
```

#### **5. 场景 4：多支路并联**

```python
def merge_parallel_branches(circuit):
    merged = {}
    for branch in circuit["branches"]:
        key = (branch["from"], branch["to"])
        if key not in merged:
            merged[key] = []
        merged[key].append(branch)

    # 计算等效导纳
    for (n1, n2), branches in merged.items():
        if len(branches) <= 1:
            continue
        Y_eq = 0+0j
        for b in branches:
            if b["type"] == "R":
                Y_eq += 1 / b["value"]
            elif b["type"] == "L":
                Y_eq += 1 / (1j * circuit["omega"] * b["value"])
            # ...其他元件类似
        print(f"并联等效 {n1}-{n2}: Y={Y_eq}")
```

---

### **三、实验总体思路总结**

#### **1. 实现步骤**

1. **输入解析**

   - 定义电路拓扑（结点、支路、元件参数）
   - 指定参考地（通常选连接支路最多的结点）

2. **矩阵构建**

   - **动态元件**：计算复数导纳（L/C 需引入`jω`）
   - **电源处理**：
     - 电流源 → 直接写入 KCL 方程右侧
     - 电压源 → 超级结点法或大数法
   - **并联支路**：合并导纳（复数相加）

3. **方程求解**

   - 解复数线性方程组 `YV = I`
   - 使用`numpy.linalg.solve`或稀疏矩阵求解器

4. **结果验证**
   - **功率守恒**：`Σ(电源输出功率) = Σ(元件消耗功率)`
   - **极限测试**：
     - 令 ω→0（直流）：电感短路、电容开路
     - 令 ω→∞：电感开路、电容短路

#### **2. 关键注意事项**

- **复数运算**：所有动态元件导纳和结果电压均为复数
- **参考结点选择**：避免选电压源正极导致方程退化
- **病态矩阵**：当存在极小/极大阻抗时，需比例缩放

#### **3. 扩展性设计**

```python
# 支持更复杂输入的改进方案
def parse_circuit(json_file):
    with open(json_file) as f:
        data = json.load(f)
        # 自动检测受控源、非线性元件等
        # 返回标准化电路描述
```

---

### **四、完整流程示例**

**输入电路**：

- N1-N2：10Ω 电阻 || 5V 电压源
- N2-N3：1μF 电容
- N3-地：2A 电流源

**伪代码执行**：

```python
Y = build_complex_matrix(circuit)  # 构建复数导纳矩阵
I = [0+0j] * 3
add_sources(Y, I, circuit)         # 添加电源影响
V = solve(Y, I)                    # 求解结点电压
print("结点电压:", V)               # 输出复数结果
```

**预期输出**：

- 直流分析（ω=0）：电容开路，N3 电压=2A×∞→ 需特殊处理
- 交流分析（ω=1000）：输出复数电压幅值和相位

---

通过这种模块化设计，你的程序可以灵活处理从简单到复杂的各种电路拓扑！
