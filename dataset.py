import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

GT = "VPR-GT-RPE-0"


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


def ids(root):
    return [s["name"] for s in json.loads((Path(root) / "setups.json").read_text())["setups"]]


def load_trajectory(root, name):
    root = Path(root)
    return Trajectory(
        name=name,
        images=sorted((root / "images" / name).glob("*.png")),
        poses=np.load(root / "poses" / f"{name}.npy"),
    )


def load(id, root, gt=GT):
    root = Path(root)
    setup = {s["name"]: s for s in json.loads((root / "setups.json").read_text())["setups"]}
    if id not in setup:
        raise KeyError(f"unknown dataset {id!r}, choose from {list(setup)}")
    s = setup[id]
    with np.load(root / "vpr_gt" / gt / f"{id}.npz") as g:
        gt_soft, gt_hard = g["gt_soft"], g["gt_hard"]
    return Dataset(
        name=id,
        db=load_trajectory(root, s["db_trajectory"]),
        query=load_trajectory(root, s["q_trajectory"]),
        gt_soft=gt_soft,
        gt_hard=gt_hard,
    )
