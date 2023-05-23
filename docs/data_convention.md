# 原子graph数据规范-v0.4beta

## data数据结构

```python
data_dict = dict{
    'x': numpy.ndarray, # 原子序数 [n_nodes,1]
    'pos': numpy.ndarray, # 原子位置 [n_nodes,3]
    **kwargs}: # 其他label
```

1. 使用dict保存

    1.1 `x`,`pos`为必须拥有的标签

    1.2 `kwargs` 保存所有其他标签

    1.3 如果包含`cell`标签,则表示该数据集具有周期性结构
    
    1.4 每个数据使用`pickle.dump()`和`pickle.load()`读写，除特殊情况外，文件名全部命名为连续的数字`{idx}.pkl`,且记数从0开始，如`0.pkl`。如有额外情况，请在[现有数据集](docs/dateset_list.md)进行相关说明.

2. 数据类型

    3.1 所有三维向量都使用行向量(靠后的index为分量的index)

    3.2 除特殊情况,所有数值都保存为`numpy.ndarray`,整数设定为`dtype=numpy.int64`,浮点数设定`dtype=numpy.float64`

    3.3 无法转为`ndarray`的变量应保存为对应`edge`或`node`长度的`list`,而不是`tuple`

3. 额外数据

    3.1 保存在`{idx}.pkl`中的属性需满足以下条件：

        3.1.1 对于数据集中的不同数据点,该属性可能不同

        3.1.2 是`str`或者`np.ndarray`(int或float等数值类型都应转为ndarray)

        3.1.3 如果是 `numpy.ndarray`，对不同数据,除了第0个维度外,应有相同的`shape`

        3.1.4 数据大小不显著超过其它属性

    3.2 不满足以上条件的数据应该储存为另外的文件
    
    3.3 如果某些属性是整个数据集所有数据共享的，则以字典的方式保存在一个`dataset_attributes.pkl`文件中

        3.3.1 通常,这个文件中必须包含你的各个属性使用了什么样的物理单位
        ```Python
        {
            'Unit':{'attr1':`Unit1`,'attr1':`Unit1`},
            ...
        }
        ```
    
    3.4 绑定到每个数据点的额外数据保存为`{idx}.{attribute_name}.pkl`。如果有某几个属性常常同时使用，可以用`dict`合并保存在单个文件中：
    ```python
    {
        'attribute1':attribute1,
        'attribute2':attribute2,
        'attribute3':attribute3,
    }
    ```

4. 命名规则

    4.1 所有与节点有关的标签命名用`node_`作为前缀,如`node_mass`

    4.2 所有与边有关的标签命名用`edge_`作为前缀,如`edge_distance`

    4.3 所有与整张图有关的标签不使用以上前缀,如`name`

    4.4 常见物理量使用统一的名称，参照[常用名称](docs/name_list.md)

    4.5 出特殊情况,所有英文字母应为小写


## 数据集

1. 目录结构

    1.1 数据集的目录结构如下所示：
    ``` 
    |-- dataset_name
    |   |-- raw
    |   |   |-- {idx}.pkl
    |   |   |-- ...
    |   |-- extra
    |   |   |-- {idx}.attr1.pkl
    |   |   |-- {idx}.attr2.pkl
    |   |   |-- ...  
    |   |-- dataset_attributes.pkl
    ```

2. 储存和读取

    2.1 一类数据集存储在ceph上的一个bucket中

        2.1.1 原子结构相同的视为同一类数据集,如`qm7`

        2.1.2 bucket命名以agdb_作为前缀，作为标准格式数据集的标记，如`agdb_qm7`

        2.1.2 同一类数据集的不同处理保存在单独的子目录中，视为一个独立数据集，子目录的命名没有强制规定。

    2.2 上传的各数据集须在[现有数据集](docs/dateset_list.md)进行相关说明

    2.3 公开数据集需配置支持匿名访问

