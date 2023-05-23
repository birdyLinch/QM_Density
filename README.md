# Atom-graph-database

本project包含:

1. [数据规范](docs/data_convention.md)
3. [常用名称](docs/name_list.md)
2. [数据集列表](docs/dateset_list.md)
3. [常用bash脚本](docs/scripts_list.md)
2. [数据工具（python module)](docs/datatools/introduction.md)

---

## Quick start

### 下载已有数据集

本项目使用ceph共享数据, 推荐使用sensesync进行数据的上传和下载,
参见[ceph使用说明](http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/01-Petrel-OSS%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/index.html)
和[sensesync使用说明](http://sdoc.pjlab.org.cn:10099/docs/hpc/usage/08-sensesync-backup.html).

所有本项目在ceph上的目录以agdb_xxxxx的方式命名,前缀agdb是**A**tom **G**raph **D**ata**B**ase的缩写.

在本教程中, 使用的示例数据集为`agdb_null_test`, ceph bucket名称为`agdb_null_test`. 包括基础数据(`raw`文件夹中), 两类额外文件`attr1`&`attr2`(`extra`文件夹中).

```bash
# files
agdb_null_test
|---raw  # basic file dir
|   |---001.pkl
|   |---002.pkl
|   |---...
|---extra  # extra file dir
|   |---001.attr1.pkl
|   |---001.attr2.pkl
|   |---002.attr1.pkl
|   |---002.attr2.pkl
|   |---...
|---dataset_attributes.pkl  # basic file
|---raw.tar  # tarfile of dir raw, optional
|---attr1.tar  # tarfile of extra/attr1, optional
|---attr2.tar  # tarfile of extra/attr2, optional
```

每个数据集都由数据集属性`dataset_attributes.pkl`和两个子目录`raw`和`extra`构成,
根据[数据规范](docs/data_convention.md), `dataset_attributes.pkl`中以`dict`的形式保存整个数据集的所有数据点共享的属性,
`raw`中的数据文件储存一个分子结构和基本的属性, 如能量等,
`extra`中的文件储存附加属性, 可以根据你的模型的实际需要按需下载和读取.
读取方式会在本教程的[读取本地数据集](#读取本地数据集)一节中介绍.

假设你现在已经配置好了sensesync,我们就可以使用如下命令下载数据:
``` bash
sensesync --anonymous 0 cp s3://agdb_null_test.10.140.2.204/ <your_data_path>/
```
这里你需要把`<your_data_path>`替换为一个具体的目录. 这样, 执行命令后所有数据文件就下载到了本地.

ceph有权限控制功能, 访问ceph上的目录需要相应的访问权限, 本教程中的数据集已经配置了允许[匿名访问](#上传新的数据集), 因此任何人都能通过匿名访问`--anonymous 0`获取.
在一般的情况下, 下载前你需要在[管理平台](petrel.pjlab.org.cn)上向数据集的拥有者申请访问权限.

### 读取本地数据集

假设我们已经下载了上一节中的`agdb_null_test`数据集, 我们先来看一下数据集里都有什么.
阅读本节时, 建议对照[数据规范](docs/data_convention.md)一起看, 本节的数据都遵循这一规范.

首先, 我们来看一下`raw`目录里有什么:

```bash
raw  # basic file dir
|---001.pkl
|---002.pkl
```

```python
# raw/001.pkl
>>> import pickle
>>> with open("<your_data_path>/raw/001.pkl") as f:
>>>     pickle.load(f)
{'x': array([1, 3, 5, 6]),
 'pos': array([[-1.63331094,  0.75480048,  0.9601171 ],
        [-0.47974295,  1.01928488, -1.20201389],
        [ 0.50422725,  2.32178196, -0.99859271],
        [-0.15990044, -1.33673388, -1.677831  ]]),
 'name': '001',
 'etol': -0.08012218238361365}
```

在`raw`目录中, 有两个`{name}.pkl`文件, 每个文件储存了一个分子的数据, 不同的分子用不同的`{name}`标记.

再看一下extra目录:

```bash
extra  # basic file dir
|---001.attr1.pkl
|---001.attr2.pkl
|---002.attr1.pkl
|---002.attr2.pkl
```

```python
# extra/0001.attr2.pkl
>>> with open("<your_data_path>/extra/001.attr1.pkl") as f:
>>>     pickle.load(f)
{'attr1_1': array([-1.66051672, -0.45761608,  0.5147151 , -1.85360247, -0.0466721 ]),
 'attr1_2': array([[-0.11453922, -0.09535394,  1.54399523],
        [-0.63859771,  1.11285543, -0.56919963],
        [-0.08672203,  1.29176386,  1.15865253],
        [-0.44347449, -0.98350267,  1.64920487],
        [-0.36067238, -0.17904819,  0.65143063]])}
```

可以看到,文件的格式为`{name}.{attr}.pkl`, 不同的额外属性使用`{attr}`的中间名标记.
每一个`.pkl`文件中可以储存多个属性, 读取的内容是一个`dict`:

```python
{  # the key has prefix {attr}, {} for domain deliminator, should be ignored
    '{attr}_{attr1}': ...,
    '{attr}_{attr2}': ...,
    '{attr}_{attr3}': ...,
    ...,
}
```

因此, 大多数时候我们其实不需要下载全部的extra数据, 只要下载`dataset_attributes.pkl`、全部的`raw`和需要的`extra`,
这可以通过sensesync的[正则表达式匹配](http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/02-Petrel-OSS%E8%BF%9B%E9%98%B6%E8%AF%B4%E6%98%8E/03-sensesync%E8%BF%9B%E9%98%B6.html#id12)功能实现.

**注:接下来的内容是使用`torch_geometric`读取数据,如果你不适用这一框架,那么你需要根据数据文件的结构自己实现读取数据的代码,你可以跳到[上传新的数据集](#上传新的数据集)继续阅读**

在我们目前的工作中,常使用`torch_geometric(pyg)`来管理图网络的数据, 我们可以尝试使用`pyg`读取这个数据集.对于标准格式的数据, 得益于数据格式的标准化, 我们提供了公共的`Dataset`类来便捷地读取数据,
代码见[datatools/datasets](datatools/pyg_datasets.py)

**注: 目前datatools还不能以python module的形式安装(正在完善), 代码的使用方式是直接复制到你的文件中**

代码中实现了三个不同的数据集类:
- `Atom_graphs_dataset`: 拥有最大的灵活度
- `InMemory_Atom_graphs_dataset`: 拥有最高的读取效率
- `Direct_Atom_graphs_dataset`: 拥有最快的初始化速度

他们都继承自`torch_geometric`的[Dataset](https://pytorch-geometric.readthedocs.io/en/latest/notes/create_dataset.html), 适用于不同的场景.
训练代码中, 我们推荐优先使用`InMemory_Atom_graphs_dataset`, 更详细的说明请参见相应的代码和注释.

使用这些代码的方式非常简单, 通常只需要两个参数`root`和`extra_attrs`:

```python
>>> root = "<your_data_path>/agdb_null_test/"
>>> dataset = InMemory_Atom_graphs_dataset(root, extra_attrs=['attr1', 'attr2'])
Processing...
Done!
```

root是你的数据所在的目录,extra_attrs是需要读取的额外属性, 即extra文件的中间名, 无论是否读取多个属性, 都要放在一个`list`中提交.

第一次运行上面的代码时, 需要比较长的时间完成数据的读取和预处理, 并将处理后的数据集保存在`root/processed/InMemoryDataset.attr1_attr2.pkl`的单个文件中, 之后再进行读取就可以几乎立即完成了. 当然, 在调试代码时, 使用`Direct_Atom_graphs_dataset`会更加方便, 它能瞬间完成初始化.

```python
>>> root = "<your_data_path>/agdb_null_test/"
>>> dataset = Direct_Atom_graphs_dataset(root, extra_attrs=['attr1', 'attr2'])
```

接下来, 你就可以直接从中读取数据, 或者将它传递给一个`Dataloader`:

```python
>>> data = dataset[0]
>>> data
Data(x=[4], pos=[4, 3], name='001', etol=-0.08012218238361365, attr1_1=[5], attr1_2=[5, 3], attr2_1=[5], attr2_2=[5, 3])
```

从`dataset_attributes.pkl`中读取的数据集公共属性属性也可以从这个`dataset`中获取:

```Python
>>> dataset.dataset_attrs
{'xc': 'm062x',
 'basis': 'def2tzvp',
 'unit': {'energy': 'eV', 'length': 'Bohr'},
 'doc': 'This is a test dataset for building agdb modules'}
```

需要特别注意的是,只有存在`raw`中的数据会被数据集自动从`numpy.ndarray`转化为`torch.Tensor`,额外数据需要自己转换,例如使用下节中介绍的`transform`.

更多细节请参考[代码](datatools/pyg_datasets.py)和[pyg的文档](https://pytorch-geometric.readthedocs.io/en/latest/modules/data.html#torch_geometric.data.Dataset)

### 使用Transform

原始的数据通常不会直接作为模型的输入, 而是需要一些预处理,
比如按照一定的方式从原子的位置`pos`生成图的边`edge_index`, 在边上生成需要的属性, 如原子间的相对距离等.
这些操作我们可以通过定义需要的[transform](https://pytorch-geometric.readthedocs.io/en/latest/notes/introduction.html#data-transforms)来完成.
`transform`既可以直接作用于单个数据, 又可以作为参数传给`Dataset`使每一个数据都自动进行transform.

在`torch_geometric`中, 已经预定义了很多实用的[transform](https://pytorch-geometric.readthedocs.io/en/latest/modules/transforms.html),
我们下面尝试为`qm7_gnnxc`添加边和相对距离:

```python
>>> from torch_geometric import transforms
>>> tf1 = transforms.RadiusGraph(r=2.5)
>>> tf2 = transforms.Distance()
>>> tf = transforms.Compose([tf1,tf2])
>>> tf(data)
Data(x=[4], pos=[4, 3], name='001', etol=-0.08012218238361365, attr1_1=[5], attr1_2=[5, 3], attr2_1=[5], attr2_2=[5, 3], edge_index=[2, 6], edge_attr=[6, 1])
```

可以看到, `Data`中多了两个属性, `edge_index`和`edge_attr`. 验证transform产生了预期的效果后, 我们可以重新定义数据集:

```python
>>> dataset_with_tf = Direct_Atom_graphs_dataset(root,extra_attrs = ['attr1','attr2'],transform=tf)
>>> dataset_with_tf[0]
Data(x=[4], pos=[4, 3], name='001', etol=-0.08012218238361365, attr1_1=[5], attr1_2=[5, 3], attr2_1=[5], attr2_2=[5, 3], edge_index=[2, 6], edge_attr=[6, 1])
```
可以看到, 现在读出来的数据使已经经过transform的.

在训练过程中, 每个数据都会被反复读取, 因此在读取之后再进行transform会产生很大的额外计算成本, 更常用的方式是在初始化数据集的时候完成需要的transform, 此时我们使用`pre_transfrom`参数来定义数据集,以完成数据的预处理. 特别地, `Direct_Atom_graphs_dataset`不支持预处理, 此时我们必须使用`InMemory_Atom_graphs_dataset`或`Atom_graphs_dataset`来读取数据:
```python
>>> dataset_with_tf = Atom_graphs_dataset(root,extra_attrs = ['attr1','attr2'],pre_transform=tf)
Processing...
Done!
>>> dataset_with_tf[0]
Data(x=[4], pos=[4, 3], name='001', etol=-0.08012218238361365, attr1_1=[5], attr1_2=[5, 3], attr2_1=[5], attr2_2=[5, 3], edge_index=[2, 6], edge_attr=[6, 1])
```

`pre_transform`和`transfrom`参数可以同时存在, 如非必要情况, 比如正在debug, 或者这个操作不能够提前完成, 我们都应该优先使用`pre_transform`.

除了使用预定义的`transfrom`外, 我们也可以自己定义任意的操作. 一个常用操作是转化数据类型.
在[数据规范](docs/data_convention.md)中, 所有的数据都是用双精度(float64/int64)储存, 提高精度的代价是更大的储存空间和更慢的训练速度.

```python
>>> data.pos.dtype
torch.float64

>>> class Change_dtype(transforms.BaseTransform):
        def __init__(self,attr_names:Union[list[str],str],dtypes:Union[list[torch.dtype],torch.dtype]) -> None:
            self.attr_names = attr_names
            self.dtypes = dtypes

        def __call__(self, data: Data) -> Data:
            if isinstance(self.attr_names,str):
                self.attr_names = [self.attr_names]
            if not isinstance(self.dtypes,list):
                self.dtypes = [self.dtypes for i in range(len(self.attr_names))]
            for name,dtype in zip(self.attr_names,self.dtypes):
                attr = getattr(data,name).to(dtype=dtype)
                setattr(data,name,attr)
            return data
>>> another_tf = Change_dtype(['x','pos'],[torch.int8,torch.float32])
>>> data = another_tf(data)
>>> data.x.dtype
torch.int8
>>> data.pos.dtype
torch.float32
```

以上代码定义了一个将指定属性转化为torch.float32类型的变换. 自定义变换时, 我们需要继承`transform.BaseTransform`类, 并定义`__init__`和`__call__`两个方法. 前者是初始化该变换的实例时调用的, 后者是对数据进行变换时调用的.


**进阶说明**

pyg的dataloader和pytorch的基础dataloader的区别是定义了一个默认的`collate_fn`,使得它能够正确地生成多个`Data`数据的Batch.但是这个默认的`collate_fn`并不总能正确地处理所有类型的数据,例如当某个属性对于不同的数据是`shape`互不相同的`torch.Tensor`时,这个函数就会报错.`agdb_null_test`中的两个额外属性就是这样的.不过,如果我们不对这些属性作类型转换,保持它们为`numpy.ndarray`,默认的`collate_fn`就能正常运行.

因此,我们不能以transfrom的形式转化这些属性,因为transform发生在collate之前,相反,我们在获取数据后手动进行transform.

### 上传新的数据集

本数据库需要大家的共同努力来丰富数据集, 在上传数据集之前, 需要大家在先在本地将数据处理为符合[数据规范](docs/data_convention.md)的标准格式. 针对不同的软件有不同的输出, 这一部分暂时没有现成的代码, 大家如果完成了某一软件的输出解析, 欢迎将自己的代码更新到datatools/data_parser中, 具体方式参考[贡献代码](#贡献代码)

完成数据的处理后, 上传到ceph, 根据数据规范, 标准化数据的桶名称应以agdb_作为前缀.
为了方便数据集管理和防止误删, 见每个数据集单独存储为一个桶.
和[下载数据](#下载已有数据集)时一样, 我们推荐使用sensesync.

```bash
# 首先创建bucket
aws --endpoint-url=http://10.140.2.204:80 s3 mb <bucket_name>
# 上传数据到刚刚创建的bucket中
sensesync cp <your_data_path>/ s3://<bucket_name>.10.140.2.204/<dataset_name>/
```

如果允许所有人访问你的数据集, 需要配置匿名访问. 配置匿名访问的第一步是编写并保存如下策略文件:
```json
{
    "Version":"2012-10-17",
    "Statement":[
    {
        "Effect":"Allow",
        "Principal":{"AWS":["arn:aws:iam:::user/anonymous"]},
        "Action":["s3:ListBucket", "s3:GetObject"],
        "Resource":["arn:aws:s3:::<bucket_name>", "arn:aws:s3:::<bucket_name>/*"]
        }
    ]
}
```
假设我们把这个文件保存为`~/anonymous.json`,运行如下命令:
```bash
aws --endpoint-url=http://10.140.2.204:80 s3api put-bucket-policy --bucket <bucket_name> --policy file://~/anonymous.json
```
注意需要修改所有<>中的内容为你起的文件名或目录名.

通过以上步骤, 就可以完成文件的上传. 但是你还需要在[数据集列表](docs/dateset_list.md)中添加这个数据集的说明内容, 让别人可以了解这个数据集的细节.
此外, 如果你第一次引入了一个新的属性, 你还应该在[常用名称](docs/name_list.md)中添加这个属性的名称和说明,
做以上步骤之前, 你需要现在群里告知大家, 经讨论无误后再实行.


### 贡献代码

每个人都可以为本项目贡献代码, 包括但不限于:

1. 某个软件的数据处理
2. 更好的数据集管理代码
3. 自动化配置环境的脚本
4. 常用的transform
5. 更详细的说明文档
6. 修复现有代码的bug

最佳的贡献方式使使用gitlab的pull request功能, 如果你不熟悉这一功能, 也可以直接提交commit到项目的dev分支
对于commit的方式, 如果你新增了不影响现有功能的代码, 可以直接发布到gitlab上, 再在群里告知.
如果你的代码会影响现有功能或者需要修改旧代码, 请先在群里与大家讨论无误后再实行.

本项目目前计划定期整理新上传的代码, 使datatools保持简洁一致的代码结构, 项目的版本号仅在每次整理后进行更新.

---

## 内置Ceph自动下载

**本部分仍在开发阶段, 目前通过测试, 后续将整合入正式的文件载入流程中**

agdb提供内置的自动下载功能, 可以根据需要自动下载相应的文件, 减少手工劳动和文件配置的困难.

- Ceph的自动下载基于[`petreloss_SDK`](http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/01-Petrel-OSS%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/02-SDK%E9%85%8D%E7%BD%AE%E4%B8%8E%E7%AE%80%E5%8D%95%E6%93%8D%E4%BD%9C.html)
或[`awscli`](http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/01-Petrel-OSS%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/01-awscli%E9%85%8D%E7%BD%AE%E4%B8%8E%E7%AE%80%E5%8D%95%E6%93%8D%E4%BD%9C.html)
    - 使用前至少安装/配置其中一个, 具体安装配置参考相应链接.

- `petreloss_SDK`
    - 基于python package (封装了awscli), 但安装python package可能遇到问题
    - 安装包可以在Ceph的bucket [`petrel-oss-python-SDK`](https://petrel.pjlab.org.cn/#/bucket-inner-file-list?bucketName=petrel-oss-python-SDK)中下载和安装
    - 必须有`petreloss.conf`配置文件
- `awscli`
    - 基于命令行因此不稳定, 安装python package较为方便
    - 依赖`~/.s3cfg`配置文件中的部分信息

### 例子

以示例数据集`agdb_null_test`为例进行演示

1. 检查`./datatools/ceph_datasets`中的配置文件, 是否有需要的数据集
    - [`agdb_null_test`的配置文件](./datatools/ceph_datasets/agdb_null_test.py)如下所示
    - 配置文件格式为Python的dict, 包括必须部分和可选部分
    - `datafiles`中指明各类数据文件以及其中的变量名称
        - 不同于文件存储中在`extra`文件夹放置各种`extra_attr`, 配置文件中`extra_attr`与`raw`同等地位

```Python
# This is a simple demonstrations of how to construct a dataset info dict.
info = {
    "author": "louzekun",  # optional
    "mail": "louzekun@pjlab.org.cn",  # optional
    "ip": "10.140.14.204:80",  # must
    "bucket": "agdb_null_test",  # must
    "count": 2,  # must
    "datafiles": {  # must, dir -> file -> Data.attrs
        "raw": ["x", "pos", "name", "etol",],
        "attr1": ["attr1_1", "attr1_2"],  # first level and second level
        "attr2": ["attr2_1", "attr2_2"],
        # NOTICE: second-level attr's names should start with their parent first-level attr
    },
    "doc": "This is a test dataset for building agdb modules",  # must
}
```

2. 进行下载

- `CEPHDataset.download()`方法中
    - `extra_attrs`: 需要的attr, 可以`attr_name`, 也可以是`.pkl`其中的变量名称
        - 若为`all`, 则下载所有文件
    - `use_tar`: 是否优先使用tar文件下载
        - tar文件打包时的命令为`cd [root]; tar -cvf [attr_name].tar ./extra/*.[attr_name].pkl`或`cd [root]; tar -cvf raw.tar ./raw/*.pkl`
        - 因此解压时将直接解压入对应的`raw`和`extra`文件见内
    - `del_tar`: 是否直接删除下载的tar文件

```Python
"""an example on downloading dataset"""
from datatools.ceph_tools import CEPHDataset  # 优先使用petreloss-SDK中的petrel_client

root = "[root]"  # 放置dataset的路径
ceph_dataset = CEPHDataset(bucket="agdb_null_test")
print(ceph_dataset.__repr__())  # CEPHDataset(name=agdb_null_test, doc=This is a test dataset for building agdb modules)
ceph_dataset.download(root=root, extra_attrs="all", use_tar=True, del_tar=True, chunk_size=100)
```

3. 使用数据集

- 见上侧





