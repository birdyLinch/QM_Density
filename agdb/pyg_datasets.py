import os
from typing import Callable, Iterable, List, Optional,Any, Tuple, Union

import numpy as np
import torch

import pickle

from torch_geometric.data import Data,Dataset,InMemoryDataset

class Atom_graphs_dataset(Dataset):

    def __init__(self, root: str , transform: Optional[Callable] = None, extra_attrs: Optional[List[str]]= None,
    pre_transform: Optional[Callable] = None, pre_filter: Optional[Callable] = None, 
    sort_key: Optional[Callable] = None):
        """Read standard agdb data

        Args:
            root (str): The path to your dataset.
            transform (Optional[Callable]): Transform that applies to your data when reading it. Defaults to None.
            extra_attrs(Optional[List[str]]): Extra atrributes that need to be read from extra file.
            pre_transform (Optional[Callable]): Transform that applies to your data when initializing the dataset. Defaults to None.
            pre_filter (Optional[Callable]): Filter to skip data with certain condition. Defaults to None.

        NOTE This dataset reads the graphs one by one, so it main have slow io speed when your graphs are small.
             In most sense, use the InMemory version below can be more efficient.
        """
        with open(os.path.join(root,"dataset_attributes.pkl"),'rb') as f:
            self.dataset_attrs = pickle.load(f)
        if extra_attrs is not None:
            self.extra_dir = os.path.join(root,'extra')
            self.extra_attrs = extra_attrs
        if sort_key is not None:
            self.sort_key = sort_key
        super().__init__(root, transform, pre_transform, pre_filter)
        self._processed_file_names = self.processed_file_names
        
    @property
    def raw_file_names(self) -> Tuple[str]:
        """if return fnames in the raw dir, one could never trigger self.download
        see Dataset._download for details"""
        fnames = [f for f in os.listdir(self.raw_dir) if f.endswith(".pkl")]
        if hasattr(self,"sort_key"):
            fnames = sorted(fnames, key=self.sort_key)
        else:
            fnames = sorted(fnames, key=lambda x: int(x.split(".")[0]))
        return fnames

    @property
    def processed_file_names(self) -> Tuple[str]:
        if hasattr(self,'extra_attrs'):
            fnames = [ #{name}.{extra_attrs}.pkl
                f"{raw_name.split('.')[0]}.{'_'.join(self.extra_attrs)}.pkl" 
                for raw_name in self.raw_file_names]
        else:
            fnames = self.raw_file_names
        return fnames

    def len(self):
        return len(self.processed_file_names)

    def get(self, idx):
        data = torch.load(os.path.join(self.processed_dir, self._processed_file_names[idx]))
        if self.transform is not None:
            data = self.transform(data)
        return data

    def process(self):
        for idx,(raw_name,processed_name) in enumerate(zip(self.raw_file_names,self.processed_file_names)):
            # TODO multi threading support
            data = self._single_process(raw_name,idx)
            if data is not None: # pre_filter may return None
                torch.save(data, os.path.join(self.processed_dir,processed_name))

    def _single_process(self,raw_name,idx):
        with open(os.path.join(self.raw_dir, raw_name),'rb') as f:
            data_dict = pickle.load(f)
        for key,val in data_dict.items():
            if isinstance(val,np.ndarray):
                data_dict[key] = torch.from_numpy(val)
        data = Data(**data_dict)
        if hasattr(self,'extra_attrs'):
            for extra_attribute in self.extra_attrs:
                with open(os.path.join(self.extra_dir, f"{raw_name.split('.')[0]}.{extra_attribute}.pkl"),'rb') as f:
                    extra = pickle.load(f)
                if isinstance(extra,dict):
                    for key,val in extra.items():
                        setattr(data,key,val)
                else:
                    setattr(data,extra_attribute,extra)

        if self.pre_filter is not None and not self.pre_filter(data):
            return None

        if self.pre_transform is not None:
            data = self.pre_transform(data)
        return data

class InMemory_Atom_graphs_dataset(InMemoryDataset):

    def __init__(self, root: str , transform: Optional[Callable] = None, extra_attrs: Optional[List[str]]= None,
    pre_transform: Optional[Callable] = None, pre_filter: Optional[Callable] = None,sort_key: Optional[Callable] = None):
        """Read standard agdb data

        Args:
            root (str): The path to your dataset.
            transform (Optional[Callable]): Transform that applies to your data when reading it. Defaults to None.
            extra_attrs(Optional[List[str]]): Extra atrributes that need to be read from extra file.
            pre_transform (Optional[Callable], optional): Transform that applies to your data when initializing the dataset. Defaults to None.
            pre_filter (Optional[Callable]): Filter to skip data with certain condition. Defaults to None.

        NOTE This dataset reads all the graphs to memory when initializing the dataset. So it may takes a longer time to initlalize,
             and may not as flexible as the former one.
        """
        with open(os.path.join(root,"dataset_attributes.pkl"),'rb') as f:
            self.dataset_attrs = pickle.load(f)
        if extra_attrs is not None:
            self.extra_dir = os.path.join(root,'extra')
            self.extra_attrs = extra_attrs
        if sort_key is not None:
            self.sort_key = sort_key
        super().__init__(root, transform, pre_transform, pre_filter)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self) -> Tuple[str]:
        """if return fnames in the raw dir, one could never trigger self.download
        see Dataset._download for details"""
        fnames = [f for f in os.listdir(self.raw_dir) if f.endswith(".pkl")]
        if hasattr(self,"sort_key"):
            fnames = sorted(fnames, key=self.sort_key)
        else:
            fnames = sorted(fnames, key=lambda x: int(x.split(".")[0]))
        return fnames

    @property
    def processed_file_names(self) -> str:
        return [f"InMemoryDataset.{'_'.join(self.extra_attrs)}.pkl"]
    
    def process(self):
        data_list = []
        for idx,raw_name in enumerate(self.raw_file_names):
            # TODO multi threading support
            data = self._single_process(raw_name,idx)
            if data is not None:
                data_list.append(data)

        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])
        
    def _single_process(self,raw_name:str,idx:int):
        with open(os.path.join(self.raw_dir, raw_name),'rb') as f:
            data_dict = pickle.load(f)
        for key,val in data_dict.items():
            if isinstance(val,np.ndarray):
                data_dict[key] = torch.from_numpy(val)
        data = Data(**data_dict)
        if hasattr(self,'extra_attrs'):
            for extra_attribute in self.extra_attrs:
                with open(os.path.join(self.extra_dir, f"{raw_name.split('.')[0]}.{extra_attribute}.pkl"),'rb') as f:
                    extra = pickle.load(f)
                if isinstance(extra,dict):
                    for key,val in extra.items():
                        setattr(data,key,val)
                else:
                    setattr(data,extra_attribute,extra)

        if self.pre_filter is not None and not self.pre_filter(data):
            return None

        if self.pre_transform is not None:
            data = self.pre_transform(data)
        return data

class Direct_Atom_graphs_dataset(Dataset):

    def __init__(self, root: str , transform: Optional[Callable] = None, extra_attrs: Optional[List[str]]= None,sort_key: Optional[Callable] = None):
        """Read standard agdb data

        Args:
            root (str): The path to your dataset.
            transform (Optional[Callable]): Transform that applies to your data when reading it. Defaults to None.
            extra_attrs(Optional[List[str]]): Extra atrributes that need to be read from extra file.

        NOTE This dataset will never pre-process the raw files. Instead, it do every operation on data when reading them.
             So it do not cost any time to initialize, but extrmely slow when reading. It's convient to use it when debugging. 
        """
        with open(os.path.join(root,"dataset_attributes.pkl"),'rb') as f:
            self.dataset_attrs = pickle.load(f)
        if extra_attrs is not None:
            self.extra_dir = os.path.join(root,'extra')
            self.extra_attrs = extra_attrs
        if sort_key is not None:
            self.sort_key = sort_key
        super().__init__(root, transform)
        self._raw_file_names = self.raw_file_names

    @property
    def raw_file_names(self) -> Tuple[str]:
        """if return fnames in the raw dir, one could never trigger self.download
        see Dataset._download for details"""
        fnames = [f for f in os.listdir(self.raw_dir) if f.endswith(".pkl")]
        if hasattr(self,"sort_key"):
            fnames = sorted(fnames, key=self.sort_key)
        else:
            fnames = sorted(fnames, key=lambda x: int(x.split(".")[0]))
        return fnames

    def len(self):
        return len(self.raw_file_names)

    def get(self, idx):
        raw_name = self._raw_file_names[idx]
        with open(os.path.join(self.raw_dir, raw_name),'rb') as f:
            data_dict = pickle.load(f)
        for key,val in data_dict.items():
            if isinstance(val,np.ndarray):
                data_dict[key] = torch.from_numpy(val)
        data = Data(**data_dict)
        if hasattr(self,'extra_attrs'):
            for extra_attribute in self.extra_attrs:
                with open(os.path.join(self.extra_dir, f"{raw_name.split('.')[0]}.{extra_attribute}.pkl"),'rb') as f:
                    extra = pickle.load(f)
                if isinstance(extra,dict):
                    for key,val in extra.items():
                        setattr(data,key,val)
                else:
                    setattr(data,extra_attribute,extra)
        return data
