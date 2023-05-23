"""
Create graph with periodic boundary conditions.
Modified based on nequip: https://github.com/mir-group/nequip/blob/main/nequip/data/AtomicData.py
"""
import time
import warnings

import numpy as np
import torch
import torch.nn.functional as F
from ase import geometry, neighborlist
from ase.io import read
from ase.io.vasp import read_vasp_out
from schnet import SchNet
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader


def neighbor_list_and_relative_vec(
        pos,
        r_max,
        self_interaction=True,
        cell=None,
        pbc=False,
        get_distances=True,
        get_vectors=False,
):
    """Create neighbor list and neighbor vectors based on radial cutoff.
    Create neighbor list (``edge_index``) and relative vectors
    (``edge_vectors``) based on radial cutoff.
    Edges are given by the following convention:
    - ``edge_index[0]`` is the *source* (convolution center).
    - ``edge_index[1]`` is the *target* (neighbor).
    Thus, ``edge_index`` has the same convention as the relative vectors:
    :math:`\\vec{r}_{source, target}`
    Args:
        pos (shape [N, 3]): Positional coordinate; Tensor or numpy array.
        r_max (float): Radial cutoff distance for neighbor finding.
        cell (numpy shape [3, 3]): Cell for periodic boundary conditions. Ignored if ``pbc == False``.
        pbc (bool or 3-tuple of bool): Whether the system is periodic in each of the three cell dimensions.
        self_interaction (bool): Whether to include same periodic image self-edges in the neighbor list.
        get_distances (bool): Whether to return edge distances.
        get_vectors (bool): Whether to return relative vectors.
    Returns:
        edge_index (torch.tensor shape [2, num_edges]): List of edges.
        edge_cell_shift (torch.tensor shape [num_edges, 3]): Relative cell shift
            vectors. Returned only if cell is not None.
        cell (torch.Tensor [3, 3]): the cell as a tensor on the correct device.
            Returned only if cell is not None.
        distances (torch.tensor shape [num_edges,]): List of edge distances.
        vectors (torch.tensor shape [num_edges, 3]): List of relative vectors.
    """
    if isinstance(pbc, bool):
        pbc = (pbc,) * 3

    # Either the position or the cell may be on the GPU as tensors
    if isinstance(pos, torch.Tensor):
        temp_pos = pos.detach().cpu().numpy()
    else:
        temp_pos = np.asarray(pos)

    # Get a cell on the CPU no matter what
    if isinstance(cell, torch.Tensor):
        temp_cell = cell.detach().cpu().numpy()
        cell_tensor = cell.to(dtype=torch.float64)
    elif cell is not None:
        temp_cell = np.asarray(cell)
        cell_tensor = torch.as_tensor(temp_cell, dtype=torch.float64)
    else:
        # ASE will "complete" this correctly.
        temp_cell = np.zeros((3, 3), dtype=torch.float64)
        cell_tensor = torch.as_tensor(temp_cell, dtype=torch.float64)

    # ASE dependent part
    temp_cell = geometry.complete_cell(temp_cell)

    first_idex, second_idex, vectors, distances, shifts = neighborlist.primitive_neighbor_list(
        "ijDdS",
        pbc,
        temp_cell,
        temp_pos,
        cutoff=float(r_max),
        self_interaction=True,
        use_scaled_positions=False,
    )

    # Eliminate true self-edges that don't cross periodic boundaries
    if not self_interaction:
        bad_edge = first_idex == second_idex
        bad_edge &= np.all(shifts == 0, axis=1)
        keep_edge = ~bad_edge
        if not np.any(keep_edge):
            raise ValueError(
                f"Every single atom has no neighbors within the cutoff r_max={r_max} (after eliminating self edges, no edges remain in this system)"
            )
        first_idex = first_idex[keep_edge]
        second_idex = second_idex[keep_edge]
        shifts = shifts[keep_edge]

    # Build output:
    edge_index = torch.vstack((torch.LongTensor(first_idex), torch.LongTensor(second_idex)))
    vectors = torch.as_tensor(vectors,dtype=torch.float64)
    distances = torch.as_tensor(distances,dtype=torch.float64)
    shifts = torch.as_tensor(shifts,dtype=torch.int)

    retvals = [edge_index, shifts, cell_tensor]
    if get_distances:
        retvals += [distances]
    if get_vectors:
        retvals += [vectors]

    return tuple(retvals)


if __name__ == '__main__':
    # atoms_all = []
    # for i in range(1, 6):
    #     aa = read_vasp_out(f'OUTCARs/{i}_OUTCAR', index=':')
    #     atoms_all.extend(aa)
    # print(len(atoms_all))
    # torch.save(atoms_all, 'data.pkl')
    # exit()

    atoms_all = read_vasp_out('OUTCAR', index=slice(1, 10))

    data_list = []
    for atoms in atoms_all:
        edge_index, shifts, cell_tensor, dists, vecs = neighbor_list_and_relative_vec(
            pos=atoms.positions, r_max=6.0, cell=atoms.cell, pbc=True, get_vectors=True
        )
        data = Data(
            x=torch.as_tensor(atoms.numbers, dtype=torch.int),
            pos=torch.as_tensor(atoms.positions, dtype=torch.float64),
            cell=torch.as_tensor(cell_tensor, dtype=torch.float64),
            edge_index=torch.as_tensor(edge_index, dtype=torch.long),
            edge_weight=torch.as_tensor(dists, dtype=torch.float32),
            edge_vecs=torch.as_tensor(vecs, dtype=torch.float32),
            shifts=torch.as_tensor(shifts, dtype=torch.int),
            energy=torch.as_tensor(atoms.calc.results['energy'], dtype=torch.float32),
            forces=torch.as_tensor(atoms.calc.results['forces'], dtype=torch.float32),
            stress=torch.as_tensor(atoms.calc.results['stress'], dtype=torch.float32),
        )
        # print(data)
        data_list.append(data)

    print(data_list[0].edge_vecs)

    # torch.save(data_list, 'data_processed.pkl')
    # exit()

    # # training
    # data_list = torch.load('data_processed.pkl')
    # dataloader = DataLoader(data_list, batch_size=1)

    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # model = SchNet().to(device)
    # optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=5e-4)

    # model.train()
    # for epoch in range(300):
    #     for data in dataloader:
    #         data = data.to(device)
    #         optimizer.zero_grad()
    #         out = model(data.x, data.pos, data.edge_index, data.edge_weight, batch=data.batch)
    #         loss = F.l1_loss(out.squeeze(), data.energy)
    #         loss.backward()
    #         optimizer.step()
    #         print(loss.item())

