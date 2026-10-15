from dataclasses import dataclass
from pathlib import Path

import numpy as np

GT = "VPR-GT-RPE-0"

# setup name -> (db trajectory, query trajectory)
SETUPS = {
    f"{db}--{q}": (db, q)
    for db, q in [
        ("MadMax-A0", "MadMax-A2"),
        ("MadMax-A2", "MadMax-A4"),
        ("MadMax-C0", "MadMax-C1"),
        ("MadMax-E0", "MadMax-E1"),
        ("MadMax-F0", "MadMax-F3"),
        ("MadMax-G0", "MadMax-G2"),
        ("S3LI-Etna-crater", "S3LI-Etna-crater_inout"),
        ("S3LI-Etna-traverse_1", "S3LI-Etna-loops"),
        ("LunarLoc-9", "LunarLoc-10"),
        ("LunarLoc-15", "LunarLoc-17"),
        ("SPICE-A-dawn-off-spad@5.0us", "SPICE-A-night-on-spad@5.0us"),
        ("SPICE-A-dawn-off@2500.0us", "SPICE-A-night-on@2500.0us"),
        ("SPICE-A-dawn-off-spad@5.0us", "SPICE-A-noon-off-spad@5.0us"),
        ("SPICE-A-dawn-off@2500.0us", "SPICE-A-noon-off@2500.0us"),
        ("SPICE-A-noon-off-spad@5.0us", "SPICE-A-night-on-spad@5.0us"),
        ("SPICE-A-noon-off@2500.0us", "SPICE-A-night-on@2500.0us"),
    ]
}


@dataclass
class Trajectory:
    name: str
    images: list[Path]
    poses: np.ndarray


@dataclass
class Dataset:
    name: str
    db: Trajectory
    query: Trajectory
    gt_soft: np.ndarray
    gt_hard: np.ndarray


def ids(root=None):
    return list(SETUPS)


def load_trajectory(root, name):
    root = Path(root)
    return Trajectory(
        name=name,
        images=sorted((root / "images" / name).glob("*.png")),
        poses=np.load(root / "poses" / f"{name}.npy"),
    )


def load(id, root, gt=GT):
    root = Path(root)
    if id not in SETUPS:
        raise KeyError(f"unknown dataset {id!r}, choose from {list(SETUPS)}")
    db, q = SETUPS[id]
    with np.load(root / "vpr_gt" / gt / f"{id}.npz") as g:
        gt_soft, gt_hard = g["gt_soft"], g["gt_hard"]
    return Dataset(
        name=id,
        db=load_trajectory(root, db),
        query=load_trajectory(root, q),
        gt_soft=gt_soft,
        gt_hard=gt_hard,
    )
