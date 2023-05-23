import torch
from torch_geometric import transforms
from torch_geometric.data import Data,Dataset
from typing import Callable, Iterable, List, Optional,Any, Tuple, Union

class Change_dtype(transforms.BaseTransform):
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