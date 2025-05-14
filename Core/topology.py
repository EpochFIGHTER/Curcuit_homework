'''
@brief 该文件定义了网络拓扑的基本结构和操作，包括节点、支路、二端元件
'''

class Node:
    '''
    @brief 节点类
    '''

    def __init__(self, num : int):
        '''
        @brief 节点类的构造函数
        @param num 节点编号
        '''
        self.num : int = num        # 节点编号，唯一
        self.branches = {}    # 支路字典，键为另一个节点，值为支路对象列表

    def __hash__(self):
        return hash(self.num)

    def __eq__(self, other):
        return self.num == other.num

    def __str__(self):
        return f"Node{self.num}"
    def __repr__(self):
        return self.__str__()

class Branch:
    '''
    @brief 支路类
    @detail 使用有头双向链表管理支路上的二端元件
    '''

    def __init__(self, node1 : Node, node2 : Node):
        '''
        @brief 支路类的构造函数
        @param node1 支路的一个节点
        @param node2 支路的另一个节点
        '''
        self.node_left : Node = node1
        if node1.branches.get(node2) is None:
            node1.branches[node2] = [self]
        else:
            node1.branches[node2].append(self)
        self.node_right : Node = node2
        if node2.branches.get(node1) is None:
            node2.branches[node1] = [self]
        else:
            node2.branches[node1].append(self)

        self.head : Component = Component(self)    # 支路头部
        self.tail : Component = Component(self)    # 支路尾部
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def insert(self, new_component, after):
        '''
        @brief 在支路中插入二端元件
        @param new_component 新插入的二端元件
        @param after 插入位置的前一个二端元件
        '''
        new_component.prev = after
        new_component.next = after.next
        after.next.prev = new_component
        after.next = new_component
        new_component.branch = self
    
    def remove(self, component):
        '''
        @brief 从支路中删除二端元件
        @param component 要删除的二端元件
        '''
        component.prev.next = component.next
        component.next.prev = component.prev
        component.prev = None
        component.next = None
        component.branch = None
    
    def append(self, new_component):
        '''
        @brief 在支路末尾添加二端元件
        @param new_component 新插入的二端元件
        '''
        self.insert(new_component, self.tail.prev)
    
    def __len__(self):
        '''
        @brief 获取支路中二端元件的数量
        @return 支路中二端元件的数量
        '''
        count = 0
        c = self.head.next
        while c != self.tail:
            count += 1
            c = c.next
        return count

    def __getitem__(self, index):
        '''
        @brief 获取支路中指定索引的二端元件
        @param index 索引
        @return 支路中指定索引的二端元件
        '''
        if index < 0:
            index = len(self) + index
        if index < 0 or index >= len(self):
            raise IndexError('Index out of range')
        c = self.head.next
        for _ in range(index):
            c = c.next
        return c

    def __iter__(self):
        c = self.head.next
        while c != self.tail:
            yield c
            c = c.next
    
    def __contains__(self, component_class):
        c = self.head.next
        while c != self.tail:
            if isinstance(c, component_class):
                return True
            c = c.next
        return False

    def __delete__(self):
        self.node_left.branches[self.node_right].remove(self)
        self.node_right.branches[self.node_left].remove(self)

    def __str__(self):
        return f"Branch({self.node_left} --- {self.node_right})"
    def __repr__(self):
        return self.__str__()

class Component:
    '''
    @brief 二端元件类
    '''

    def __init__(self, branch=None):
        '''
        @brief 二端元件类的构造函数
        @param branch 所在支路
        @param prefix 二端元件的前缀，为None表示不需要编号
        '''
        self.prev : Component = None     # 上一个二端元件
        self.next : Component = None     # 下一个二端元件
        self.branch : Branch = branch    # 所在支路

    def join(self, branch):
        '''
        @brief 将二端元件加入支路
        @param branch 要加入的支路
        '''
        branch.append(self)

    def leave(self):
        '''
        @brief 将二端元件从支路中移除
        '''
        self.branch.remove(self)

    def move_left(self):
        '''
        @brief 将二端元件向左移动一个位置
        '''
        if self.prev is not None:
            b = self.branch
            p = self.prev
            self.leave()
            b.insert(self, p.prev)
    
    def move_right(self):
        '''
        @brief 将二端元件向右移动一个位置
        '''
        if self.next is not None:
            b = self.branch
            n = self.next
            self.leave()
            b.insert(self, n)
    
    def get_index(self):
        '''
        @brief 获取二端元件在支路中的索引
        @return 二端元件在支路中的索引
        '''
        index = 0
        c = self.branch.head.next
        while c != self.branch.tail:
            if c == self:
                return index
            c = c.next
            index += 1
    
    def __str__(self):
        return f"{self.name}"
    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    # 测试代码
    n1 = Node(1)
    n2 = Node(2)
    b = Branch(n1, n2)
    c1 = Component(b)
    c2 = Component(b)
    c3 = Component(b)
    b.append(c1)
    b.append(c2)
    b.append(c3)
    c3.move_left()
    print(b)
    print(len(b))
    print(b[0])
    print(b[1])
    for c in b:
        print(c)
