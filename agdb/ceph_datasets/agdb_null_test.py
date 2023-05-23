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
