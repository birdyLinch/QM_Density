# Changelog

## [0.4.0] - 2023-1-17

### Added

- datatools/ceph_tools
    - `CMDClients`
    - `CEPHDataset`
- pip install support

### Changed

- rename `datatools` as `agdb`
- add cephtools introduction in `Quick start`
- bug fix in `pyg_datasets`

## [0.3.2] - 2023-01-11

### changed

- fix `Quick start`
- rename `datatools/datasets` as `datatools/pyg_datasets`
- update `datatools/pyg_datasets`
- update `data_convention`


## [0.3.1] - 2023-01-11

### Added

- prepare for packaging into a module
- add `null_test` data

### changed

- change `pyg.data.Data` and `torch.Tensor` to `dict` and `numpy.array`
- update qm7_gnnxc dataset
- kwarg `extra_attributes` to `extra_attrs` for simplicity

## [0.3] - 2023-01-10

### Added

- datatools/datasets:
    - `Atom_graphs_dataset`
    - `InMemory_Atom_graphs_dataset`
    - `Direct_Atom_graphs_dataset`
- Quick Start
    - README中的教程
    - 示例数据集`qm7_gnnxc`和`qm7_scf_M062X_6311`
    - name_list.md 和 Dataset_list.md 的示例

### Changed

- 更新了数据约定
    - 去除了部分未确定的内容
    - 额外数据的使用规则和储存方式
    - dataset的命名规则和目录结构
    - ceph的使用方式
- 删除了datatools/from_pyscf.py


## [0.2] - 2022-12-08

### Added

- 本项目框架
    - TODO 
    - Changelog
    - /docs
    - /datatools
    - /scripts

### Changed

- 更新了数据约定
    - Data中，Cell变为Optional
    - 增加数据集约定


## [0.1] - 2022-12-07

### Added

- 数据约定：Data基本数据结构