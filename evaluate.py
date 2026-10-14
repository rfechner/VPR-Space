import argparse
import json

import numpy as np

from dataset import ids, load
from methods import METHODS, Method
from metrics import auprc, recall_at_100_precision, recall_at_k


def similarity(db, query):
    mean, scale = db.mean(0), 1 / (db.std(0) + 1e-8)
    db, query = (db - mean) * scale, (query - mean) * scale
    db /= np.linalg.norm(db, axis=1, keepdims=True)
    query /= np.linalg.norm(query, axis=1, keepdims=True)
    return db @ query.T


def evaluate(S, gt_soft, gt_hard, ks=(1, 5, 10)):
    return {
        "AUPRC": auprc(S, gt_hard, gt_soft),
        "R@100p": recall_at_100_precision(S, gt_hard, gt_soft),
        **{f"R@{k}": recall_at_k(S, gt_hard, gt_soft, k) for k in ks},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--method", required=True, choices=sorted(METHODS))
    ap.add_argument("--datasets", nargs="*")
    args = ap.parse_args()

    method = Method(args.method)
    features = {}
    results = {}
    for id in args.datasets or ids(args.root):
        d = load(id, args.root)
        for t in (d.db, d.query):
            if t.name not in features:
                features[t.name] = method(t.images)
        S = similarity(features[d.db.name], features[d.query.name])
        results[id] = evaluate(S, d.gt_soft, d.gt_hard)
        print(id, " ".join(f"{k} {v:.4f}" for k, v in results[id].items()), flush=True)
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
