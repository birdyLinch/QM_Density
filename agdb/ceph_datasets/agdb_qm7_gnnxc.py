info = {
    "author": "louzekun",
    "mail": "louzekun@pjlab.org.cn",
    "ip": "10.140.2.204:80",
    "bucket": "agdb_qm7_gnnxc",
    "count": 7165,
    "datafiles": {  # dir -> file -> Data.attrs
        "raw": ["name", "x", "pos", "etol",],
        "grids": ["grids_level", "grids_coords", "grids_weights", "grids_exc", "grids_rho",],
        "scf": ["scf_rho", "scf_vxc",],
    },
    "doc": """
This is a qm7 dataset calculated by pyscf, with xc=m062x, basis=def2tzvp, grids_level=3.
The dataset is used for training the GNNXC module.
extra:
- grids: the quadrature grids used for spatial numerical integral
- scf: quantities obtained by scf calculation
    - `scf_rho`: electron density matrix
    - `scf_vxc`: XC functional of the `scf_rho`, lives in atomic orbitals
    """,
}