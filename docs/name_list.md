# 常用名称

- This list indicates the naming conventions for `pyg.data.Data` class.
- Please check [Dat_convension](https://gitlab.pjlab.org.cn/hugengyuan/atom-graph-database/-/blob/main/docs/Data_convension.md) page.


## general conventions

- data type:
    - prefer `float64`
- unit:
    - prefer Atomic Unit, like `Bohr` for length
- string:
    - use only lower case in strings
    - underline `_` for string segmentation


## dataset file structure
```bash
dataset_name
|-- raw
|   |-- [name].pkl
|   |-- [name].pkl
|   |-- ...
|-- extra
|   |-- [name].[attr].pkl
|   |-- [name].[attr].pkl
|   |-- ...
|-- dataset_attributes.pkl
```

## dataset shared info
- file name: `dataset_attributes.pkl`
- type: `dict` preferred
- `xc: str`
    - exchange-correlation functional name
    - suggest use lowercase.
    - e.g., `m062x`
- `basis: str`
    - basis function or basis details
    - e.g., `def2tzvp`, `6-311g++`
    - for more details and avaiable basis sets, see [PySCF_doc/Molecular_structure/basis_set](https://pyscf.org/user/gto.html#basis-set)
- `unit: dict`
    - the units used in the dataset
    - e.g. `{"energy": "eV", "length": "Bohr"}`
- `doc: str`
    - additional descriptions on the dataset
    - e.g. `"The dataset is maintained by xxx, please contact at xxx@xxx.xxx"`

## dir `raw` files
- type: `pyg.data.Data`

### global
- `name: str`
    - could include dataset name, item name
    - suggest same to the name in file name `[name].pkl` at dir `raw`
    - e.g.,  `qm7_0103` or simply `0103`
- `cell: Optional[torch.Tensor]`, shape `(3, 3)`
    - crystal cell edge vector
    - each row for each edge vector
    - null for moleculars, thus `Optional`
- `etol: Optional[torch.float64]`
    - directly from SCF calculation, unit is `eV`
- `edis: Optional[torch.float64]`
    - dissociation energy, per molecule or per unit cell
    - `etol` subtract single atomic energy
- ...

### node_attr
- `x: torch.Tensor(dtype=torch.int64)`
    - atomic numbers
- `pos: torch.Tensor`, shape `(natm, 3)`
    - atoms' spatial position, unit `Bohr` perfered
- ...

### edge_attr
- `edge_index: Optional[torch.Tensor(dtype=torch.int64)]`, shape `(2, edge_cnt)`
    - edges in the graph
    - could generate on the fly
- ...


## dir `extra` files
- with file name suffix `.[attr].pkl`
- type: `dict`

### grids
- file name: `[name].grids.pkl`
- `grids_: torch.Tensor`, as prefix
    - `grids_level: torch.int64`
        - For pyscf, it measures how fine the grids are.
    - `grids_coords`: shape `(grids_cnt, 3)`
        - spatial grid coordinates
        - generally large, consider store in additional files
    - `grids_weights`: shape `(grids_cnt, )`
        - spatial grid integrate weights
        - generally large, consider store in additional files
    - `grids_rho`: shape `(grids_cnt, n)`
        - electron density on grids
        - n could be `null` for only density, `4` for density and gradients, `6` for mGGA type XC input, `20`...
        - see [pyscf.dft.numint.eval_rho](https://github.com/pyscf/pyscf/blob/master/pyscf/dft/numint.py#L116) for detailed conventions
    - `grids_exc`: shape `(grids_cnt, )`
        - spatial XC functional kernel
            - spatial XC energy density divided by spatial electron density
        - PySCF: $f^R (r) = \frac{E^{XC}(r)}{\rho(r)} = $ `ni.eval_xc()[0]`
    - `grids_[vxc, vrho, vgamma, vlapl, vtau, fxc, kxc]`: shape `grids_cnt`
        - for evaluating  XC matrix
        - for details, see [pyscf.dft.libxc.eval_xc](https://github.com/pyscf/pyscf/blob/master/pyscf/dft/libxc.py#L1333)
    - `grids_excrho`: shape `(ngrids, n)`
        - spatial XC energy density
        - could be obtained from $f^R (r) \rho(r)$

### scf
- file name: `[name].scf.pkl`
- `scf_: torch.Tensor`, as prefix
    - quantities from scf iterations
        - should be calculated with `basis` and `xc`
    - `scf_rho`, electron density matrix
    - `scf_vxc`, XC energy density matrix


### [attr]
- file name: `[name].[attr].pkl`
- `[attr]_: dtype`
    - explaination
    - `[attr]_[xxx]`, explaination
    - ...




