"""General utils"""
from pathlib import Path


def log(msg):
    print(msg)


def rm(f):
    p = Path(f)
    if p.exists():
        p.unlink()


def clean_dir(raw_path):
    dir_path = Path(raw_path)
    if dir_path.exists():
        for f in dir_path.glob('*'):
            f.unlink()
    else:
        dir_path.mkdir()
