#   =====================================================================
#   Copyright (C) 2023  Stefan Schubert, stefan.schubert@etit.tu-chemnitz.de
#   This program is free software under the GNU General Public License v3+.
#   See <http://www.gnu.org/licenses/>. (metric primitives only)
#   =====================================================================

import numpy as np


def createPR(S_in, GThard, GTsoft=None, n_thresh=100):
    GT = GThard.astype(bool)
    S = S_in.copy()
    if GTsoft is not None:
        S[GTsoft.astype(bool) & ~GT] = S.min()
    GTP = np.count_nonzero(GT)

    R = [0]
    P = [1]
    for i in np.linspace(S.max(), S.min(), n_thresh):
        B = S >= i
        TP = np.count_nonzero(GT & B)
        FP = np.count_nonzero((~GT) & B)
        P.append(TP / (TP + FP))
        R.append(TP / GTP)
    return P, R


def recallAtK(S, GT, K=1):
    GT = GT.astype(bool)
    j = GT.sum(0) > 0
    S = S[:, j]
    GT = GT[:, j]
    i = S.argsort(0)[-K:, :]
    j = np.tile(np.arange(i.shape[1]), [K, 1])
    GT = GT[i, j]
    return np.sum(GT.sum(0) > 0) / GT.shape[1]


def auprc(S, gt_hard, gt_soft):
    P, R = createPR(S, gt_hard, gt_soft)
    return float(np.trapezoid(P, R))


def recall_at_100_precision(S, gt_hard, gt_soft):
    P, R = map(np.asarray, createPR(S, gt_hard, gt_soft))
    at100 = R[P == 1]
    return float(at100.max()) if at100.size else 0.0


def recall_at_k(S, gt_hard, gt_soft, k):
    return float(recallAtK(S, gt_hard | gt_soft, K=k))
