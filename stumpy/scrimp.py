# STUMPY
# Copyright 2019 TD Ameritrade. Released under the terms of the 3-Clause BSD license.
# STUMPY is a trademark of TD Ameritrade IP Company, Inc. All rights reserved.

import logging

import numpy as np
from numba import njit, prange, config

from . import core

logger = logging.getLogger(__name__)


@njit(fastmath=True)
def _get_max_order_idx(m, n, orders, start, percentage):
    """
    Determine the order index for when the desired percentage of distances is computed

     Parameters
    ----------
    m : int
        Window size

    n : int
        Matrix profile length

    orders : ndarray
        The order of diagonals to process and compute

    start : int
        The (inclusive) order index from which to start

    percentage : float
        Approximate percentage completed. The value is between 0.0 and 1.0.

    Returns
    -------
    max_order_id : int
        The order index that corresponds to desired percentage of distances to compute

    n_dist_computed : int
        The number of distances computed
    """

    max_n_dist = 0
    for order_idx in range(orders.shape[0]):
        k = orders[order_idx]
        max_n_dist = max_n_dist + (n - m + 2 - k)

    n_dist_computed = 0
    for order_idx in range(start, orders.shape[0]):
        k = orders[order_idx]
        n_dist_computed = n_dist_computed + (n - m + 2 - k)
        if n_dist_computed / max_n_dist > percentage:  # pragma: no cover
            break

    max_order_idx = order_idx + 1

    return max_order_idx, n_dist_computed


@njit(fastmath=True)
def _get_orders_ranges(n_split, m, n, orders, start, percentage):
    """
    For the desired percentage of distances to be computed from orders, split the
    orders into `n_split` chunks, and determine the appropriate start and stop
    (exclusive) order index ranges for each chunk

     Parameters
    ----------
    n_split : int
        The number of chunks to split the percentage of desired orders into

    m : int
        Window size

    n : int
        Matrix profile length

    orders : ndarray
        The order of diagonals to process and compute

    start : int
        The (inclusive) order index from which to start

    percentage : float
        Approximate percentage completed. The value is between 0.0 and 1.0.

    Returns
    -------
    ranges : int
        The start (column 1) and (exclusive) stop (column 2) orders index ranges
        that corresponds to a desired percentage of distances to compute
    """

    max_order_idx, n_dist_computed = _get_max_order_idx(m, n, orders, start, percentage)

    orders_ranges = np.zeros((n_split, 2), np.int64)
    ranges_idx = 0
    range_start_idx = start
    max_n_dist_per_range = n_dist_computed / n_split

    n_dist_computed = 0
    for order_idx in range(start, max_order_idx):
        k = orders[order_idx]
        n_dist_computed = n_dist_computed + (n - m + 2 - k)
        if n_dist_computed > max_n_dist_per_range:  # pragma: no cover
            orders_ranges[ranges_idx, 0] = range_start_idx
            orders_ranges[ranges_idx, 1] = min(
                order_idx + 1, max_order_idx
            )  # Exclusive stop index
            # Reset and Update
            range_start_idx = order_idx + 1
            ranges_idx += 1
            n_dist_computed = 0
    # Handle final range outside of for loop
    orders_ranges[ranges_idx, 0] = range_start_idx
    orders_ranges[ranges_idx, 1] = max_order_idx

    return orders_ranges


@njit(fastmath=True)
def _compute_diagonal(
    T, m, μ, σ, orders, orders_start_idx, orders_stop_idx, excl_zone, thread_idx, P, I
):
    """
    Compute (Numba JIT-compiled) and update P, I along a single diagonal using a single
    thread and avoiding race conditions

    Parameters
    ----------
    T : ndarray
        The time series or sequence for which to compute the matrix profile

    m : int
        Window size

    μ : ndarray
        Sliding window mean for T

    σ : ndarray
        Sliding window standard deviation for T

    orders : ndarray
        The order of diagonals to process and compute

    orders_start_idx : int
        The start index for a range of diagonal order to process and compute

    orders_stop_idx : int
        The (exclusive) stop index for a range of diagonal order to process and compute

    excl_zone : int
        The half width for the exclusion zone relative to the current
        sliding window

    P : ndarray
        Matrix profile

    I : ndarray
        Matrix profile indices

    Returns
    -------
    None
    """
    n = T.shape[0]

    for order_idx in range(orders_start_idx, orders_stop_idx):
        k = orders[order_idx]
        for i in range(0, n - m + 2 - k):
            if i == 0:
                QT = np.dot(T[i : i + m], T[i + k - 1 : i + k - 1 + m])
            else:
                QT = QT - T[i - 1] * T[i + k - 2] + T[i + m - 1] * T[i + k + m - 2]

            D_squared = core._calculate_squared_distance(
                m, QT, μ[i], σ[i], μ[i + k - 1], σ[i + k - 1],
            )

            if i < i + k - 1 - excl_zone and D_squared < P[thread_idx, i]:
                P[thread_idx, i] = D_squared
                I[thread_idx, i] = i + k - 1

            if i < i + k - 1 - excl_zone and D_squared < P[thread_idx, i + k - 1]:
                P[thread_idx, i + k - 1] = D_squared
                I[thread_idx, i + k - 1] = i


@njit(parallel=True, fastmath=True)
def _scrimp(T, m, μ, σ, orders, orders_ranges, excl_zone, percentage=0.1):
    """
    A Numba JIT-compiled version of SCRIMP (self-join) for parallel computation
    of the matrix profile and matrix profile indices.

    Parameters
    ----------
    T : ndarray
        The time series or sequence for which to compute the matrix profile

    m : int
        Window size

    μ : ndarray
        Sliding window mean for T

    σ : ndarray
        Sliding window standard deviation for T

    orders : ndarray
        The order of diagonals to process and compute

    ranges : ndarray
        The start (column 1) and (exclusive) stop (column 2) order indices for
        each thread

    excl_zone : int
        The half width for the exclusion zone relative to the current
        sliding window

    percentage : float
        Approximate percentage completed. The value is between 0.0 and 1.0.

    Returns
    -------
    P : ndarray
        Matrix profile

    I : ndarray
        Matrix profile indices

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00099 \
    <https://www.cs.ucr.edu/~eamonn/SCRIMP_ICDM_camera_ready_updated.pdf>`__

    See Algorithm 1
    """

    n = T.shape[0]
    l = n - m + 1
    n_threads = config.NUMBA_NUM_THREADS
    P = np.empty((n_threads, l))
    I = np.empty((n_threads, l), np.int64)

    P[:, :] = np.inf
    I[:, :] = -1

    for thread_idx in prange(n_threads):
        # Compute and pdate P, I within a single thread while avoiding race conditions
        _compute_diagonal(
            T,
            m,
            μ,
            σ,
            orders,
            orders_ranges[thread_idx, 0],
            orders_ranges[thread_idx, 1],
            excl_zone,
            thread_idx,
            P,
            I,
        )

    # Reduction of results from all threads
    for thread_idx in range(1, n_threads):
        for i in prange(l):
            if P[0, i] > P[thread_idx, i]:
                P[0, i] = P[thread_idx, i]
                I[0, i] = I[thread_idx, i]

    return np.sqrt(P[0]), I[0]


def _prescrimp(T, m, μ, σ, s=None):
    """
    A NumPy implementation of the preSCRIMP algorithm.

    Parameters
    ----------
    T : ndarray
        The time series or sequence for which to compute the matrix profile

    m : int
        Window size

    μ : ndarray
        Sliding window mean for T

    σ : ndarray
        Sliding window standard deviation for T

    s : int
        The sampling interval that defaults to `int(np.ceil(m / 4))`

    Returns
    -------
    P : ndarray
        Matrix profile

    I : ndarray
        Matrix profile indices

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00099 \
    <https://www.cs.ucr.edu/~eamonn/SCRIMP_ICDM_camera_ready_updated.pdf>`__

    See Algorithm 2
    """

    n = T.shape[0]
    l = n - m + 1
    P = np.empty(l)
    I = np.empty(l, np.int64)
    excl_zone = int(np.ceil(m / 4))

    if s is None:  # pragma: no cover
        s = excl_zone

    P[:] = np.inf
    I[:] = -1

    for i in np.random.permutation(range(0, l, s)):
        Q = T[i : i + m]

        # Update P[i] relative to all T[j : j + m]
        D_squared = np.square(core.mass(Q, T, μ, σ))  # Use squared distances
        zone_start = max(0, i - excl_zone)
        zone_stop = min(l, i + excl_zone)
        D_squared[zone_start : zone_stop + 1] = np.inf
        I[i] = np.argmin(D_squared)
        P[i] = D_squared[I[i]]
        if P[i] == np.inf:  # pragma: no cover
            I[i] = -1

        # Update all P[j] relative to T[i : i + m] as this is still relevant info
        # Note that this was not in the original paper but was included in the C++ code
        for j in range(l):
            if D_squared[j] < P[j]:
                P[j] = D_squared[j]
                I[j] = i

        j = I[i]
        # Given the squared distance, work backwards and compute QT
        QT = (m - P[i] / 2.0) * (σ[i] * σ[j]) + (m * μ[i] * μ[j])
        QT_prime = QT
        for k in range(1, min(s, l - max(i, j))):
            QT = QT - T[i + k - 1] * T[j + k - 1] + T[i + k + m - 1] * T[j + k + m - 1]
            D_squared = core._calculate_squared_distance(
                m, QT, μ[i + k], σ[i + k], μ[j + k], σ[j + k],
            )
            if D_squared < P[i + k]:
                P[i + k] = D_squared
                I[i + k] = j + k
            if D_squared < P[j + k]:
                P[j + k] = D_squared
                I[j + k] = i + k
        QT = QT_prime
        for k in range(1, min(s, i + 1, j + 1)):
            QT = QT - T[i - k + m] * T[j - k + m] + T[i - k] * T[j - k]
            D_squared = core._calculate_squared_distance(
                m, QT, μ[i - k], σ[i - k], μ[j - k], σ[j - k],
            )
            if D_squared < P[i - k]:
                P[i - k] = D_squared
                I[i - k] = j - k
            if D_squared < P[j - k]:
                P[j - k] = D_squared
                I[j - k] = i - k

    return np.sqrt(P), I


def scrimp(T, m, percentage=0.01, prescrimp=False, s=None):
    """
    Compute the matrix profile with parallelized SCRIMP (self-join). This returns a
    generator that can be incrementally iterated on. For SCRIMP++, set
    `prescrimp=True`.

    This is a convenience wrapper around the Numba JIT-compiled parallelized
    `_scrimp` function which computes the matrix profile according to SCRIMP.

    Parameters
    ----------
    T : ndarray
        The time series or sequence for which to compute the matrix profile

    m : int
        Window size

    percentage : float
        Approximate percentage completed. The value is between 0.0 and 1.0.

    prescrimp : bool
        A flag for whether or not to perform the PreSCRIMP calculation prior to
        computing SCRIMP. If set to `True`, this is equivalent to computing
        SCRIMP++

    s : int
        The size of the PreSCRIMP fixed interval. If `prescrimp=True` and `s=None`,
        then `s` will automatically be set to `s=int(np.ceil(m/4))`, the size of
        the exclusion zone.

    Returns
    -------
    out : ndarray
        Matrix profile and matrix profile indices

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00099 \
    <https://www.cs.ucr.edu/~eamonn/SCRIMP_ICDM_camera_ready_updated.pdf>`__

    See Algorithm 1
    """

    T = np.asarray(T)
    T = T.copy()
    T[np.isinf(T)] = np.nan
    core.check_dtype(T)

    if T.ndim != 1:  # pragma: no cover
        raise ValueError(f"T is {T.ndim}-dimensional and must be 1-dimensional. ")

    core.check_window_size(m)

    n = T.shape[0]
    l = n - m + 1
    out = np.empty((l, 2), dtype=object)
    out[:, 0] = np.inf
    out[:, 1] = -1

    μ, σ = core.compute_mean_std(T, m)
    T[np.isnan(T)] = 0
    excl_zone = int(np.ceil(m / 4))

    if s is None:
        s = excl_zone

    if prescrimp:
        P, I = _prescrimp(T, m, μ, σ, s)
        for i in range(P.shape[0]):
            if out[i, 0] > P[i]:
                out[i, 0] = P[i]
                out[i, 1] = I[i]

    orders = np.random.permutation(range(excl_zone + 1, n - m + 2))
    n_threads = config.NUMBA_NUM_THREADS
    percentage = min(percentage, 1.0)
    percentage = max(percentage, 0.0)
    generator_rounds = int(np.ceil(1.0 / percentage))
    start = 0
    for round in range(generator_rounds):
        orders_ranges = _get_orders_ranges(n_threads, m, n, orders, start, percentage)

        P, I = _scrimp(T, m, μ, σ, orders, orders_ranges, excl_zone, percentage)
        start = orders_ranges[:, 1].max()

        # Update matrix profile and indices
        for i in range(out.shape[0]):
            if out[i, 0] > P[i]:
                out[i, 0] = P[i]
                out[i, 1] = I[i]

        yield out
