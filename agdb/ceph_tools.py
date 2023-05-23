import configparser
import datetime
import importlib
import locale
import logging
import os
import re
import shlex
import shutil
import subprocess
import tarfile
from functools import partial
from typing import Any, Dict, Generator, List, Literal, Union

from tqdm import tqdm

# if use petrel_client
USE_PETRELCLIENT:bool=None
# config petreloss
PETRELOSSCONFDOC:str = r"http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/01-Petrel-OSS%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/02-SDK%E9%85%8D%E7%BD%AE%E4%B8%8E%E7%AE%80%E5%8D%95%E6%93%8D%E4%BD%9C.html#id3"
# config aws s3
AWSS3CONFDOC:str = r"http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/01-Petrel-OSS%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/01-awscli%E9%85%8D%E7%BD%AE%E4%B8%8E%E7%AE%80%E5%8D%95%E6%93%8D%E4%BD%9C.html#id1"
# # system encoding
# ENC:str = locale.getpreferredencoding()  # get local encoding

# try to import petrel_client
try:
    import petrel_client
    from botocore.response import StreamingBody
    from petrel_client.client import Client
    from petrel_client.mixed_client import MixedClient
    USE_PETRELCLIENT = True
except ImportError:
    logging.warning("Module petrel_client not found, using CMDClient as alternative. To install petrel_client, see http://sdoc.pjlab.org.cn:10099/docs/Petrel-OSS/ for instructions")
    USE_PETRELCLIENT = False


"""
aws s3 behaviors:

ls:
- bucket
    - exists: content
    - exists / empty: nothing
    - nonexists: error, return 255
- content
    - no end `/`:
        - has dir: print dir info
        - has file: print file info
    - end with `/`:
        - has dir: print dir content info
        - no dir: error, return code 1
"""

class CMDClient:
    """provide same methods as petrel_client.client.Client
    based on aws s3 cmdlines ans regex parsing
    please refer to petrel_client.mixed_client.MixedClient for details"""

    AWS_PRE:str = "aws s3 --endpoint-url=http://10.140.2.204:80"

    PAT = {  # regex patterns
        "list": r"""
            ^([\d\-]*)\s?([\d:]*)  # datetime, optional
            \s+
            (\d+|PRE)  # size
            \s
            ([.\-\w\d]+/*)$  # fname
        """,
    }

    def __init__(self, conf_path:str=None):
        # use petreloss config or aws s3 config
        if conf_path is not None:
            logging.warning("conf_path should be None when using CMDClient, auto use ~/.s3cfg as config file")
        self.conf_path = os.path.join(os.path.expanduser("~"), ".s3cfg")
        self._check_aws_s3()
        logging.info("Using commandline-based awscli as ceph client, please make sure that awscli module is at system path")

    # def __del__(self):
    #     pass

    def _execmd(self, cmd:str, **kwargs):
        """execute a cmd and return output with decoded str"""
        if type(cmd) is str:
            cmd = shlex.split(cmd)
        elif type(cmd) is not list:
            raise TypeError(f"{cmd=} should be str or list, not {type(cmd)}")
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while process.poll() is None:  # wait for procedure ends
            continue
        output = process.stdout.read().decode(locale.getpreferredencoding())
        return process.returncode, output

    def _check_aws_s3(self):
        """determine endpoint-url in the conf_path
        by `aws s3 ls --endpoint-url=xxx` cmd"""
        if not os.path.exists(self.conf_path):
            raise ValueError(f"conf_path {self.conf_path} not found, please refer to {AWSS3CONFDOC} for details")

        # get endpoint config
        config = configparser.ConfigParser()
        config.read(self.conf_path, encoding=locale.getpreferredencoding())
        try:
            host_base = config.get("default", "host_base")
        except configparser.NoOptionError:
            raise ValueError(f"default/host_base not found .s3cfg, which is necessary")
        assert host_base.startswith("http://")
        self.AWS_PRE = f"aws s3 --endpoint-url={host_base}"

        # try exe a aws cmd
        cmd = f"{self.AWS_PRE} ls"
        c, s = self._execmd(cmd)
        assert c == 0, f"command `{cmd}` failed, please (re)install awscli and refer to {AWSS3CONFDOC} for details"
        return True

    def _check_uri(self, uri:str):
        """check if uri is of correct formats"""
        if not uri.startswith("s3://"):
            return False
        else:
            return True

    def _ls(self, uri:str):
        cmd = f"{self.AWS_PRE} ls {uri}"
        c, s = self._execmd(cmd)
        assert c == 0, f"command `{cmd}` failed"
        regex = re.compile(self.PAT["list"], re.VERBOSE)
        matches = [regex.search(ss) for ss in s.splitlines()]
        return [m.groups() for m in matches]  # date, time, size, fname

    def create_bucket(self, bucket:str, **kwargs):
        """create a bucket
        format of bucket: 's3://mybucket' with no ending slash"""
        assert bucket.startswith("s3://")
        assert '/' not in bucket[len("s3://"): ]
        cmd = f"{self.AWS_PRE} mb {bucket}"
        c, s = self._execmd(cmd)
        assert c == 0, f"command `{cmd}` failed"
        return c, s

    def list(self, uri:str) -> Generator:
        """list dir of this uri"""
        if not uri.endswith('/'):
            uri += '/'
        groups = self._ls(uri)
        fnames = [g[3] for g in groups]
        return fnames

    def contains(self, uri:str, **kwargs) -> bool:
        """if dir or file exists"""
        uri = uri.strip('/')
        cmd = f"{self.AWS_PRE} ls {uri}"
        c, s = self._execmd(cmd)
        if c != 0:
            return False
        else:
            return True

    def isdir(self, uri:str, **kwargs):
        """if dir exists, buckets are also dirs
        if is dir, return True
        else (e.g. non exist or file), return False"""
        assert self._check_uri(uri)
        uri = uri.rstrip("/")  # remove the right /
        if '/' not in uri[len("s3://"): ]:  # bucket
            cmd = f"{self.AWS_PRE} ls {uri}"
            c, s = self._execmd(cmd)
            if c != 0:
                return False
            else:
                return True
        else:  # dir or file
            name = uri.rsplit('/')[-1]
            uri2 = uri.rsplit('/', 1)[0]  # the parent uri
            uri2 += '/'
            groups = self._ls(uri2)
            for g in groups:
                if g[3].rstrip('/') == name:  # found
                    if g[2] == "PRE":  # is dir
                        return True
                    else:  # not dir
                        return False
            return False

    def delete(self, uri:str, **kwargs):
        """delete files"""
        raise NotImplementedError

    def get(self, uri:str, save_dir:str="./", **kwargs):
        """download files to save_dir"""
        cmd = f"{self.AWS_PRE} cp {uri} {save_dir}"
        c, s = self._execmd(cmd)
        assert c == 0, f"command `{cmd}` failed"
        return c, s


class CEPHDataset:
    """download proper files to dataset root dir from ceph"""

    # ceph_datasets.info members:
    author:str
    mail:str
    ip:str
    bucket:str
    count:int
    datafiles:Dict
    doc:str

    def __init__(self, bucket:str, conf_path:str=None):
        """load dataset info from python files of THIS name
        the bucket should exists in ceph

        Args:
            root (str): root dir of dataset, samilar meaning to pyg.data.Dataset(root)
            bucket (str): bucket name, should be exactly the same as the name of the bucket in ceph
            conf_path (str, optional): aws s3 config path. Defaults to None.
        """

        try:
            _info = importlib.import_module(f"ceph_datasets.{bucket}").info
        except:
            raise ValueError(f"Dataset {bucket} not found in ceph_dataset infomation files")
        assert _info["bucket"] == bucket
        # set info to internal attributes
        [setattr(self, k, v) for k, v in _info.items()]
        # instantialize petrel_client
        self.client = Client(conf_path=conf_path) if USE_PETRELCLIENT else CMDClient(conf_path=conf_path)
        # check if bucket exists
        assert self.client.isdir(f"s3://{bucket}"), f"bucket {bucket} not found in ceph"

    def __repr__(self):
        return f"CEPHDataset(name={self.bucket}, doc={self.doc})"

    def __doc__(self):
        return self.doc

    def get_fnames(self, attr:str) -> List[str]:
        """load single files list
        attr: None for check raw"""
        if attr == "raw":
            flist = tuple(i for i in self.client.list(f"s3://{self.bucket}/raw/") if i.endswith(".pkl"))
        elif type(attr) is str:
            extra_suffix = f".{attr}."  # the attr suffix, .[attr].
            flist = tuple(i for i in self.client.list(f"s3://{self.bucket}/extra/") if (extra_suffix in i))
        else:
            raise ValueError(f"attr should be 'raw' or str, got {attr=} with type {type(attr)}")
        if len(flist) == 0:
            raise ValueError(f"no ceph files found for {attr=}")
        return flist

    def check_bucket(self):
        """check bucket contents

        Returns:
            storage = {
                "raw": [has_single_file, has_tar_file],
                "attr1": [has_single_file, has_tar_file],
                "attr2": [has_single_file, has_tar_file],
                ...
            }
        """

        storage = {k: [None, None] for k in self.datafiles.keys()}
        for k in storage.keys():
            storage[k][0] = (self.count == len(self.get_fnames(k)))
            storage[k][1] = self.client.contains(f"s3://{self.bucket}/{k}.tar")

        # self.storage = storage
        return storage

    def _download_single(self, root:str, save_fpath:str, bucket_fpath:str, chunk_size:int=100):
        """stream download single file from bucket_fpath to save_fpath

        Args:
            root (str): dataset root to save files
            save_fpath (str): from dataset root, e.g. data/agdb_null_test/raw/001.pkl -> save_fpath='raw/001.pkl'
            bucket_fpath (str): from bucket root, e.g. bucket/raw/001.pkl -> bucket_fpath='raw/001.pkl'
            chunk_size (int, optional): chunk size in MB. Defaults to 100.

        """
        if type(self.client) is Client:
            stream:StreamingBody = self.client.get(f"s3://{self.bucket}/{bucket_fpath}", enable_stream=True)
            with open(os.path.join(root, save_fpath), 'wb') as f:
                for chunk in stream.iter_chunks(chunk_size*1024**2):
                    f.write(chunk)
        elif type(self.client) is CMDClient:
            self.client.get(f"s3://{self.bucket}/{bucket_fpath}", os.path.join(root, save_fpath))

    def download(
        self, root:str,
        extra_attrs:Union[List[str], None, Literal["all"]],
        use_tar:bool=True,
        del_tar:bool=True,
        chunk_size:int=100):
        """download data from ceph to root dir

        Args:
            root (str): root dir to the dataset
            extra_attrs (Union[List[str], None, Literal["all"]]): extra attrs to download.
                None for no extra attrs, "all" for all avaliable extra attrs.
            use_tar (bool): download tarfile instead of single files if avaliable. Defaults to True.
            del_tar (bool): delete tarfile after download. Defaults to True.
            chunk_size (int): stream download size, MB. Only effective to petrel_client. Defaults to 100.
        Returns:
            None
        """
        download_single = lambda x, y: self._download_single(root=root, save_fpath=x, bucket_fpath=y, chunk_size=chunk_size)
        global tqdm
        tqdm = partial(tqdm, ncols=100)

        check_root_dirs(root)
        extra_info = self.datafiles.copy()
        extra_info.pop("raw")
        extra_attr1s = find_extra_attr1s(extra_info, extra_attrs)  # 1 for first-level attr categories
        logging.info(f"extra_attr files: {extra_attr1s}")

        """download: 'raw' and first-level extra_attr, tar or single files, and dataset_attributes.pkl"""
        tar_fpaths = []
        # download dataset_attributes.pkl
        download_single("dataset_attributes.pkl", "dataset_attributes.pkl")

        # download raw
        if use_tar and self.client.contains(f"s3://{self.bucket}/raw.tar"):
            logging.info(f"downloading raw.tar")
            download_single("raw.tar", "raw.tar")
            tar_fpaths.append("raw.tar")
            extract_tar(os.path.join(root, "raw.tar"), root)
        else:
            fnames = self.get_fnames("raw")
            tbar = tqdm(fnames, desc="downloading raw files")
            for fname in tbar:
                download_single(os.path.join('raw', fname), os.path.join('raw', fname))

        # download extra
        for extra_attr1 in extra_attr1s:
            if use_tar and self.client.contains(f"s3://{self.bucket}/{extra_attr1}.tar"):
                logging.info(f"downloading {extra_attr1}.tar")
                download_single(os.path.join(f"{extra_attr1}.tar"), f"{extra_attr1}.tar")
                tar_fpaths.append(f"{extra_attr1}.tar")
                extract_tar(os.path.join(root, f"{extra_attr1}.tar"), root)
            else:
                fnames = self.get_fnames(extra_attr1)
                tbar = tqdm(fnames, desc=f"downloading {extra_attr1} files")
                for fname in tbar:
                    download_single(os.path.join('extra', fname), os.path.join('extra', fname))

        # remove tar files
        if del_tar:
            [os.remove(os.path.join(root, f)) for f in tar_fpaths]

        logging.info(f"Done!")

    def upload(self, root:str, use_tar:bool=True, test:bool=False):
        """upload local data"""
        raise NotImplementedError

    def fly(self, root:str):
        """load data on the fly
        consider mount ceph to the root dir"""
        raise NotImplementedError



def extract_tar(fpath_tar:str, extract_dir:str):
    """extract tar file to root dir"""
    try:
        tarobj = tarfile.open(fpath_tar)
    except tarfile.TarError:
        raise OSError(
            "%s is not a compressed or uncompressed tar file" % fpath_tar)
    try:
        tarobj.extractall(extract_dir)
    finally:
        tarobj.close()


def check_root_dirs(root:str):
    """check if root, raw, extra dir exists, or create them"""
    if not os.path.exists(root):
        os.mkdir(root)
        logging.info(f"Created dir {root}")
    for d in ["raw", "extra"]:
        dir_path = os.path.join(root, d)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
            logging.info(f"Created dir {dir_path}")


def find_extra_attr1s(extra_info:Dict[str, List[str]], extra_attrs:Union[List[str], None, Literal["all"]]) -> List[str]:
    """find first level extra files' names by comparing extra_info and extra_attrs

    Args:
        extra_info (Dict[str, List[str]]): information about dataset extra attrs.
        extra_attrs (Union[List[str], None, Literal["all"]]): required extra attributes, first-level or second-level attrs.
            None for no extra attrs, "all" for all avaliable extra attrs.
    Returns:
        List[str]: extra file names
    """
    if extra_attrs is None:
        return []
    elif (type(extra_attrs) == str) and (extra_attrs == "all"):
        return list(extra_info.keys())

    # common situations
    assert type(extra_attrs) is list
    extra_fnames = []
    for extra_attr in extra_attrs:
        found_attr = False  # record if found attr
        # iterate over the first level and second level attrs
        for attr1, attr2s in extra_info.items():
            if (extra_attr == attr1) or (extra_attr in attr2s):
                extra_fnames.append(attr1)
                found_attr = True
                continue
        if not found_attr:
            raise ValueError(f"extra attr {extra_attr} not found in dataset, with avaliable extra attrs {extra_info}")

    extra_fnames = list(set(extra_fnames))  # eliminate multiplicity
    return extra_fnames


def _test2():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s',)

    root = "/nvme/louzekun/Downloads/agdb_qm7_gnnxc"
    if os.path.exists(root):
        shutil.rmtree(root)
        logging.info(f"delete root dir {root}")

    ceph_dataset = CEPHDataset(bucket="agdb_qm7_gnnxc")
    logging.info(ceph_dataset.__repr__())
    logging.info(ceph_dataset.__doc__())
    ceph_dataset.check_bucket()
    ceph_dataset.download(root=root, use_tar=True, extra_attrs=["scf_rho"], chunk_size=100)


def _test1():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s',)

    root = "/nvme/louzekun/atom-graph-database/datatools/ceph_datasets/agdb_null_test_downloads"
    if os.path.exists(root):
        shutil.rmtree(root)
        logging.info(f"delete root dir {root}")

    ceph_dataset = CEPHDataset(bucket="agdb_null_test")
    logging.info(ceph_dataset.__repr__())
    logging.info(ceph_dataset.__doc__())
    ceph_dataset.check_bucket()
    ceph_dataset.download(root=root, use_tar=False, extra_attrs="all", chunk_size=100)
    ceph_dataset.download(root=root, use_tar=True, extra_attrs="all", chunk_size=100)

    # os.rmdir(root)

def _test2():
    global USE_PETRELCLIENT
    USE_PETRELCLIENT = False
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s',)

    root = "/nvme/louzekun/atom-graph-database/datatools/ceph_datasets/agdb_null_test_downloads"
    if os.path.exists(root):
        shutil.rmtree(root)
        logging.info(f"delete root dir {root}")

    ceph_dataset = CEPHDataset(bucket="agdb_null_test")
    logging.info(ceph_dataset.__repr__())
    logging.info(ceph_dataset.__doc__())
    ceph_dataset.check_bucket()
    ceph_dataset.download(root=root, use_tar=False, extra_attrs="all", chunk_size=100)
    ceph_dataset.download(root=root, use_tar=True, extra_attrs="all", chunk_size=100)


if __name__ == "__main__":
    _test1()
    _test2()


