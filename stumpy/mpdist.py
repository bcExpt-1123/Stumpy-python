# STUMPY
# Copyright 2019 TD Ameritrade. Released under the terms of the 3-Clause BSD license.
# STUMPY is a trademark of TD Ameritrade IP Company, Inc. All rights reserved.

import numpy as np
import math

from . import stump, stumped


def _compute_P_ABBA(
    T_A, T_B, m, P_ABBA, dask_client=None, device_id=None, mp_func=stump
):
    """
    A convenience function for computing the (unsorted) concatenated matrix profiles
    from an AB-join and BA-join for the two time series, `T_A` and `T_B`. This result
    can then be used to compute the matrix profile distance (MPdist) measure.

    The MPdist distance measure considers two time series to be similar if they share
    many subsequences, regardless of the order of matching subsequences. MPdist
    concatenates and sorts the output of an AB-join and a BA-join and returns the value
    of the `k`th smallest number as the reported distance. Note that MPdist is a
    measure and not a metric. Therefore, it does not obey the triangular inequality but
    the method is highly scalable.

    Parameters
    ----------
    T_A : ndarray
        The first time series or sequence for which to compute the matrix profile

    T_B : ndarray
        The second time series or sequence for which to compute the matrix profile

    m : int
        Window size

    P_ABBA : ndarray
        The output array to write the concatenated AB-join and BA-join results to

    dask_client : client, default None
        A Dask Distributed client that is connected to a Dask scheduler and
        Dask workers. Setting up a Dask distributed cluster is beyond the
        scope of this library. Please refer to the Dask Distributed
        documentation.

    device_id : int or list, default None
        The (GPU) device number to use. The default value is `0`. A list of
        valid device ids (int) may also be provided for parallel GPU-STUMP
        computation. A list of all valid device ids can be obtained by
        executing `[device.id for device in numba.cuda.list_devices()]`.

    mp_func : object, default stump
        Specify a custom matrix profile function to use for computing matrix profiles

    Returns
    -------
    None

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00119 \
    <https://www.cs.ucr.edu/~eamonn/MPdist_Expanded.pdf>`__

    See Section III
    """
    n_A = T_A.shape[0]

    if dask_client is not None:
        P_ABBA[: n_A - m + 1] = mp_func(dask_client, T_A, m, T_B, ignore_trivial=False)[
            :, 0
        ]
        P_ABBA[n_A - m + 1 :] = mp_func(dask_client, T_B, m, T_A, ignore_trivial=False)[
            :, 0
        ]
    elif device_id is not None:
        P_ABBA[: n_A - m + 1] = mp_func(
            T_A, m, T_B, ignore_trivial=False, device_id=device_id
        )[:, 0]
        P_ABBA[n_A - m + 1 :] = mp_func(
            T_B, m, T_A, ignore_trivial=False, device_id=device_id
        )[:, 0]
    else:
        P_ABBA[: n_A - m + 1] = mp_func(T_A, m, T_B, ignore_trivial=False)[:, 0]
        P_ABBA[n_A - m + 1 :] = mp_func(T_B, m, T_A, ignore_trivial=False)[:, 0]


def _select_P_ABBA_value(P_ABBA, k=None, custom_func=None):
    """
    A convenience function for returning the `k`th smallest value from the `P_ABBA`
    array or use a custom function to specify what `P_ABBA` value to return.

    The MPdist distance measure considers two time series to be similar if they share
    many subsequences, regardless of the order of matching subsequences. MPdist
    concatenates and sorts the output of an AB-join and a BA-join and returns the value
    of the `k`th smallest number as the reported distance. Note that MPdist is a
    measure and not a metric. Therefore, it does not obey the triangular inequality but
    the method is highly scalable.

    Parameters
    ----------
    P_ABBA : ndarray
        A pre-sorted array resulting from the concatenation of the outputs from an
        AB-joinand BA-join for two time series, `T_A` and `T_B`

    k : int, default None
        Specify the `k`th value in the concatenated matrix profiles to return. This
        parameter is ignored when `k_func` is not None.

    custom_func : object, default None
        A custom user defined function for selecting the desired value from the
        sorted `P_ABBA` array. This function may need to leverage `functools.partial`
        and should take `P_ABBA` as its only input parameter and return a single
        `MPdist` value. The `percentage` and `k` parameters are ignored when
        `custom_func` is not None.

    Returns
    -------
    MPdist : float
        The matrix profile distance
    """
    if custom_func is not None:
        MPdist = custom_func(P_ABBA)
    else:
        MPdist = P_ABBA[k]
        if ~np.isfinite(MPdist):
            k = max(0, np.count_nonzero(np.isfinite(P_ABBA[:k])) - 1)
            MPdist = P_ABBA[k]

    return MPdist


def _mpdist(
    T_A,
    T_B,
    m,
    percentage=0.05,
    k=None,
    dask_client=None,
    device_id=None,
    mp_func=stump,
    custom_func=None,
):
    """
    A convenience function for computing the matrix profile distance (MPdist) measure
    between any two time series.

    The MPdist distance measure considers two time series to be similar if they share
    many subsequences, regardless of the order of matching subsequences. MPdist
    concatenates and sorts the output of an AB-join and a BA-join and returns the value
    of the `k`th smallest number as the reported distance. Note that MPdist is a
    measure and not a metric. Therefore, it does not obey the triangular inequality but
    the method is highly scalable.

    Parameters
    ----------
    T_A : ndarray
        The first time series or sequence for which to compute the matrix profile

    T_B : ndarray
        The second time series or sequence for which to compute the matrix profile

    m : int
        Window size

    percentage : float, 0.05
       The percentage of distances that will be used to report `mpdist`. The value
        is between 0.0 and 1.0. This parameter is ignored when `k` is not `None` or when
        `k_func` is not None.

    k : int, default None
        Specify the `k`th value in the concatenated matrix profiles to return. When `k`
        is not `None`, then the `percentage` parameter is ignored. This parameter is
        ignored when `k_func` is not None.

    dask_client : client, default None
        A Dask Distributed client that is connected to a Dask scheduler and
        Dask workers. Setting up a Dask distributed cluster is beyond the
        scope of this library. Please refer to the Dask Distributed
        documentation.

    device_id : int or list, default None
        The (GPU) device number to use. The default value is `0`. A list of
        valid device ids (int) may also be provided for parallel GPU-STUMP
        computation. A list of all valid device ids can be obtained by
        executing `[device.id for device in numba.cuda.list_devices()]`.

    mp_func : object, default stump
        Specify a custom matrix profile function to use for computing matrix profiles

    custom_func : object, default None
        A custom user defined function for selecting the desired value from the
        sorted `P_ABBA` array. This function may need to leverage `functools.partial`
        and should take `P_ABBA` as its only input parameter and return a single
        `MPdist` value. The `percentage` and `k` parameters are ignored when
        `custom_func` is not None.

    Returns
    -------
    MPdist : float
        The matrix profile distance

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00119 \
    <https://www.cs.ucr.edu/~eamonn/MPdist_Expanded.pdf>`__

    See Section III
    """
    n_A = T_A.shape[0]
    n_B = T_B.shape[0]
    P_ABBA = np.empty(n_A - m + 1 + n_B - m + 1, dtype=np.float64)

    _compute_P_ABBA(T_A, T_B, m, P_ABBA, dask_client, device_id, mp_func)
    P_ABBA.sort()

    if k is not None:
        k = int(k)
    else:
        percentage = min(percentage, 1.0)
        percentage = max(percentage, 0.0)
        k = min(math.ceil(percentage * (n_A + n_B)), n_A - m + 1 + n_B - m + 1 - 1)

    MPdist = _select_P_ABBA_value(P_ABBA, k, custom_func)

    return MPdist


def mpdist(T_A, T_B, m, percentage=0.05, k=None):
    """
    Compute the matrix profile distance (MPdist) measure between any two time series
    with `stumpy.stump`.

    The MPdist distance measure considers two time series to be similar if they share
    many subsequences, regardless of the order of matching subsequences. MPdist
    concatenates and sorts the output of an AB-join and a BA-join and returns the value
    of the `k`th smallest number as the reported distance. Note that MPdist is a
    measure and not a metric. Therefore, it does not obey the triangular inequality but
    the method is highly scalable.

    Parameters
    ----------
    T_A : ndarray
        The first time series or sequence for which to compute the matrix profile

    T_B : ndarray
        The second time series or sequence for which to compute the matrix profile

    m : int
        Window size

    percentage : float, default 0.05
        The percentage of distances that will be used to report `mpdist`. The value
        is between 0.0 and 1.0.

    Returns
    -------
    MPdist : float
        The matrix profile distance

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00119 \
    <https://www.cs.ucr.edu/~eamonn/MPdist_Expanded.pdf>`__

    See Section III
    """
    return _mpdist(T_A, T_B, m, percentage, k, mp_func=stump)


def mpdisted(dask_client, T_A, T_B, m, percentage=0.05, k=None):
    """
    Compute the matrix profile distance (MPdist) measure between any two time series
    with a distributed dask cluster and `stumpy.stumped`.

    The MPdist distance measure considers two time series to be similar if they share
    many subsequences, regardless of the order of matching subsequences. MPdist
    concatenates and sorts the output of an AB-join and a BA-join and returns the value
    of the `k`th smallest number as the reported distance. Note that MPdist is a
    measure and not a metric. Therefore, it does not obey the triangular inequality but
    the method is highly scalable.

    Parameters
    ----------
    dask_client : client
        A Dask Distributed client that is connected to a Dask scheduler and
        Dask workers. Setting up a Dask distributed cluster is beyond the
        scope of this library. Please refer to the Dask Distributed
        documentation.

    T_A : ndarray
        The first time series or sequence for which to compute the matrix profile

    T_B : ndarray
        The second time series or sequence for which to compute the matrix profile

    m : int
        Window size

    percentage : float, default 0.05
        The percentage of distances that will be used to report `mpdist`. The value
        is between 0.0 and 1.0. This parameter is ignored when `k` is not `None`.

    k : int
        Specify the `k`th value in the concatenated matrix profiles to return. When `k`
        is not `None`, then the `percentage` parameter is ignored.

    Returns
    -------
    MPdist : float
        The matrix profile distance

    Notes
    -----
    `DOI: 10.1109/ICDM.2018.00119 \
    <https://www.cs.ucr.edu/~eamonn/MPdist_Expanded.pdf>`__

    See Section III
    """
    return _mpdist(T_A, T_B, m, percentage, k, dask_client=dask_client, mp_func=stumped)
