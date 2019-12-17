.. image:: https://img.shields.io/pypi/v/stumpy.svg
    :target: https://pypi.org/project/stumpy/
    :alt: PyPI Version
.. image:: https://pepy.tech/badge/stumpy
    :target: https://pepy.tech/project/stumpy
    :alt: PyPI Downloads
.. image:: https://anaconda.org/conda-forge/stumpy/badges/version.svg
    :target: https://anaconda.org/conda-forge/stumpy
    :alt: Conda-forge Version
.. image:: https://anaconda.org/conda-forge/stumpy/badges/downloads.svg
    :target: https://anaconda.org/conda-forge/stumpy
    :alt: Conda-forge Downloads
.. image:: https://img.shields.io/pypi/l/stumpy.svg
    :target: https://github.com/TDAmeritrade/stumpy/blob/master/LICENSE.txt
    :alt: License
.. image:: https://dev.azure.com/stumpy-dev/stumpy/_apis/build/status/TDAmeritrade.stumpy?branchName=master
    :target: https://dev.azure.com/stumpy-dev/stumpy/_build/latest?definitionId=2&branchName=master
    :alt: Build Status
.. image:: https://readthedocs.org/projects/stumpy/badge/?version=latest
    :target: https://stumpy.readthedocs.io/
    :alt: ReadTheDocs Status
.. image:: https://codecov.io/gh/TDAmeritrade/stumpy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/TDAmeritrade/stumpy
    :alt: Code Coverage
.. image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/TDAmeritrade/stumpy/master?filepath=notebooks
    :alt: Binder
.. image:: http://joss.theoj.org/papers/10.21105/joss.01504/status.svg
    :target: https://doi.org/10.21105/joss.01504
    :alt: JOSS
.. image:: https://zenodo.org/badge/184809315.svg
    :target: https://zenodo.org/badge/latestdoi/184809315
    :alt: DOI
.. image:: https://app.fossa.com/api/projects/custom%2B9056%2Fgithub.com%2FTDAmeritrade%2Fstumpy.svg?type=shield
    :target: https://app.fossa.io/projects/custom%2B9056%2Fgithub.com%2FTDAmeritrade%2Fstumpy?ref=badge_shield
    :alt: FOSSA
.. image:: https://img.shields.io/twitter/follow/stumpy_dev.svg?style=social
    :target: https://twitter.com/stumpy_dev
    :alt: Twitter

|

.. image:: https://raw.githubusercontent.com/TDAmeritrade/stumpy/master/docs/images/stumpy_logo_small.png
    :target: https://github.com/TDAmeritrade/stumpy
    :alt: STUMPY Logo

======
STUMPY
======

STUMPY is a powerful and scalable library that efficiently computes something called the `matrix profile <https://stumpy.readthedocs.io/en/latest/Tutorial_The_Matrix_Profile.html>`__, which can be used for a variety of time series data mining tasks such as:

* pattern/motif (approximately repeated subsequences within a longer time series) discovery
* anomaly/novelty (discord) discovery
* shapelet discovery
* semantic segmentation 
* density estimation
* time series chains (temporally ordered set of subsequence patterns)
* `and more ... <https://www.cs.ucr.edu/~eamonn/100_Time_Series_Data_Mining_Questions__with_Answers.pdf>`__

Whether you are an academic, data scientist, software developer, or time series enthusiast, STUMPY is straightforward to install and allows you to compute the `matrix profile <https://stumpy.readthedocs.io/en/latest/Tutorial_The_Matrix_Profile.html>`__ in the most efficient way. Our goal is to allow you to get to your time series insights faster. See `documentation <https://stumpy.readthedocs.io/en/latest/>`__ for more information.

-------------------------
How to use STUMPY
-------------------------

Please see our `API documentation <https://stumpy.readthedocs.io/en/latest/api.html>`__ for a complete list of available functions and see our informative `tutorials <https://stumpy.readthedocs.io/en/latest/tutorials.html>`__ for more comprehensive example use cases. Below, you will find code snippets that quickly demonstrate how to use STUMPY.

Typical usage (1-dimensional time series data) with `STUMP <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.stump>`__:

.. code:: python

    import stumpy
    import numpy as np
    
    your_time_series = np.random.rand(10000)
    window_size = 50  # Approximately, how many data points might be found in a pattern 
    
    matrix_profile = stumpy.stump(your_time_series, m=window_size)

Distributed usage for 1-dimensional time series data with Dask Distributed via `STUMPED <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.stumped>`__:

.. code:: python

    import stumpy
    import numpy as np
    from dask.distributed import Client
    dask_client = Client()
    
    your_time_series = np.random.rand(10000)
    window_size = 50  # Approximately, how many data points might be found in a pattern 
    
    matrix_profile = stumpy.stumped(dask_client, your_time_series, m=window_size)

GPU usage for 1-dimensional time series data with `GPU-STUMP <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.gpu_stump>`__:

.. code:: python

    import stumpy
    import numpy as np

    your_time_series = np.random.rand(10000)
    window_size = 50  # Approximately, how many data points might be found in a pattern

    matrix_profile = stumpy.gpu_stump(your_time_series, m=window_size)

Multi-dimensional time series data with `MSTUMP <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.mstump>`__:

.. code:: python

    import stumpy
    import numpy as np

    your_time_series = np.random.rand(3, 1000)  # Each row represents data from a different dimension while each column represents data from the same dimension
    window_size = 50  # Approximately, how many data points might be found in a pattern

    matrix_profile, matrix_profile_indices = stumpy.mstump(your_time_series, m=window_size)

Distributed multi-dimensional time series data analysis with Dask Distributed `MSTUMPED <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.mstumped>`__:

.. code:: python

    import stumpy
    import numpy as np
    from dask.distributed import Client
    dask_client = Client()

    your_time_series = np.random.rand(3, 1000)   # Each row represents data from a different dimension while each column represents data from the same dimension
    window_size = 50  # Approximately, how many data points might be found in a pattern

    matrix_profile, matrix_profile_indices = stumpy.mstumped(dask_client, your_time_series, m=window_size)

Time Series Chains with `Anchored Time Series Chains (ATSC) <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.atsc>`__:

.. code:: python

    import stumpy
    import numpy as np
    
    your_time_series = np.random.rand(10000)
    window_size = 50  # Approximately, how many data points might be found in a pattern 
    
    matrix_profile = stumpy.stump(your_time_series, m=window_size)

    left_matrix_profile_index = matrix_profile[:, 2]
    right_matrix_profile_index = matrix_profile[:, 3]
    idx = 10  # Subsequence index for which to retrieve the anchored time series chain for

    anchored_chain = stumpy.atsc(left_matrix_profile_index, right_matrix_profile_index, idx)

    all_chain_set, longest_unanchored_chain = stumpy.allc(left_matrix_profile_index, right_matrix_profile_index)

Semantic Segmentation with `Fast Low-cost Unipotent Semantic Segmentation (FLUSS) <https://stumpy.readthedocs.io/en/latest/api.html#stumpy.fluss>`__:

.. code:: python

    import stumpy
    import numpy as np

    your_time_series = np.random.rand(10000)
    window_size = 50  # Approximately, how many data points might be found in a pattern

    matrix_profile = stumpy.stump(your_time_series, m=window_size)

    subseq_len = 50
    correct_arc_curve, regime_locations = stumpy.fluss(matrix_profile[:, 1], 
                                                       L=subseq_len, 
                                                       n_regimes=2, 
                                                       excl_factor=1
                                                      )

------------
Dependencies
------------

* `NumPy <http://www.numpy.org/>`__
* `Numba <http://numba.pydata.org/>`__
* `SciPy <https://www.scipy.org/>`__

---------------
Where to get it
---------------

Conda install (preferred):

.. code:: bash
    
    conda install -c conda-forge stumpy

PyPI install, presuming you have numpy, scipy, and numba installed: 

.. code:: bash

    python -m pip install stumpy

To install stumpy from source, see the instructions in the `documentation <https://stumpy.readthedocs.io/en/latest/install.html>`__.

-------------
Documentation
-------------

In order to fully understand and appreciate the underlying algorithms and applications, it is imperative that you read the original publications_. For a more detailed example of how to use STUMPY please consult the latest `documentation <https://stumpy.readthedocs.io/en/latest/>`__ or explore the following tutorials:

1. `The Matrix Profile <https://stumpy.readthedocs.io/en/latest/Tutorial_The_Matrix_Profile.html>`__
2. `STUMPY Basics <https://stumpy.readthedocs.io/en/latest/Tutorial_STUMPY_Basics.html>`__
3. `Time Series Chains <https://stumpy.readthedocs.io/en/latest/Tutorial_Time_Series_Chains.html>`__
4. `Semantic Segmentation <https://stumpy.readthedocs.io/en/latest/Tutorial_Semantic_Segmentation.html>`__

-----------
Performance
-----------

We tested the performance using the Numba JIT compiled version of the code on randomly generated data with various lengths (i.e., ``np.random.rand(n)``). 

.. image:: https://raw.githubusercontent.com/TDAmeritrade/stumpy/master/docs/images/performance.png
    :alt: STUMPY Performance Plot

The raw results are displayed below as Hours:Minutes:Seconds and with a constant window size of `m = 50`.

+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
|    i     |  n = 2\ :sup:`i`  | GPU-STOMP    | STUMP.16    | STUMPED.128 | STUMPED.256 | GPU-STUMP.1 | GPU-STUMP.2 |
+==========+===================+==============+=============+=============+=============+=============+=============+
| 6        | 64                | 00:00:10.00  | 00:00:00.00 | 00:00:05.77 | 00:00:06.08 | 00:00:00.02 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 7        | 128               | 00:00:10.00  | 00:00:00.00 | 00:00:05.93 | 00:00:07.29 | 00:00:00.03 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 8        | 256               | 00:00:10.00  | 00:00:00.01 | 00:00:05.95 | 00:00:07.59 | 00:00:00.06 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 9        | 512               | 00:00:10.00  | 00:00:00.02 | 00:00:05.97 | 00:00:07.47 | 00:00:00.11 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 10       | 1024              | 00:00:10.00  | 00:00:00.04 | 00:00:05.69 | 00:00:07.64 | 00:00:00.22 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 11       | 2048              | NaN          | 00:00:00.09 | 00:00:05.60 | 00:00:07.83 | 00:00:00.44 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 12       | 4096              | NaN          | 00:00:00.19 | 00:00:06.26 | 00:00:07.90 | 00:00:00.91 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 13       | 8192              | NaN          | 00:00:00.41 | 00:00:06.29 | 00:00:07.73 | 00:00:01.86 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 14       | 16384             | NaN          | 00:00:00.99 | 00:00:06.24 | 00:00:08.18 | 00:00:03.54 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 15       | 32768             | NaN          | 00:00:02.39 | 00:00:06.48 | 00:00:08.29 | 00:00:07.11 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 16       | 65536             | NaN          | 00:00:06.42 | 00:00:07.33 | 00:00:09.01 | 00:00:14.57 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 17       | 131072            | 00:00:10.00  | 00:00:19.52 | 00:00:09.75 | 00:00:10.53 | 00:00:28.48 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 18       | 262144            | 00:00:18.00  | 00:01:08.44 | 00:00:33.38 | 00:00:24.07 | 00:00:56.83 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 19       | 524288            | 00:00:46.00  | 00:03:56.82 | 00:01:35.27 | 00:03:43.66 | 00:01:55.29 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 20       | 1048576           | 00:02:30.00  | 00:19:54.75 | 00:04:37.15 | 00:03:01.16 | 00:04:48.73 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 21       | 2097152           | 00:09:15.00  | 03:05:07.64 | 00:13:36.51 | 00:08:47.47 | 00:19:18.96 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 22       | 4194304           | NaN          | 10:37:51.21 | 00:55:44.43 | 00:32:06.70 | 01:16:55.88 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 23       | 8388608           | NaN          | 38:42:51.42 | 03:33:30.53 | 02:00:49.37 | 05:08:57.37 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 24       | 16777216          | NaN          | NaN         | 13:03:43.86 | 07:13:47.12 | 20:31:56.07 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| NaN      | 17729800          | 09:16:12.00  | NaN         | NaN         | 07:18:42.54 | 22:51:51.05 | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 25       | 33554432          | NaN          | NaN         | NaN         | 26:27:41.29 | NaN         | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 26       | 67108864          | NaN          | NaN         | NaN         | 106:40:17.17| NaN         | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| NaN      | 100000000         | 291:07:12.00 | NaN         | NaN         | 234:51:35.39| NaN         | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+
| 27       | 134217728         | NaN          | NaN         | NaN         | NaN         | NaN         | NaN         |
+----------+-------------------+--------------+-------------+-------------+-------------+-------------+-------------+

GPU-STOMP: Results are reproduced from the original `Matrix Profile II <https://ieeexplore.ieee.org/abstract/document/7837898>`__ paper - NVIDIA Tesla K80 (contains 2 GPUs) 
    
STUMP.16: 16 CPUs in Total - 16x Intel(R) Xeon(R) CPU E5-2650 v4 @ 2.20GHz processors parallelized with Numba on a single server without Dask.

STUMPED.128: 128 CPUs in Total - 8x Intel(R) Xeon(R) CPU E5-2650 v4 @ 2.20GHz processors x 16 servers, parallelized with Numba, and distributed with Dask Distributed.

STUMPED.256: 256 CPUs in Total - 8x Intel(R) Xeon(R) CPU E5-2650 v4 @ 2.20GHz processors x 32 servers, parallelized with Numba, and distributed with Dask Distributed.

GPU-STUMP.1: 1x NVIDIA GeForce GTX 1080 Ti GPU, 512 threads per block 

GPU-STUMP.2: 2x NVIDIA GeForce GTX 1080 Ti GPU, 512 threads per block

-------------
Running Tests
-------------

Tests are written in the ``tests`` directory and processed using `PyTest <https://docs.pytest.org/en/latest/>`__ and requires ``coverage.py`` for code coverage analysis. Tests can be executed with:

.. code:: bash

    ./test.sh

--------------
Python Version
--------------

STUMPY supports `Python 3.6+ <https://python3statement.org/>`__ and, due to the use of unicode variable names/identifiers, is not compatible with Python 2.x. Given the small dependencies, STUMPY may work on older versions of Python but this is beyond the scope of our support and we strongly recommend that you upgrade to the most recent version of Python.

------------
Getting Help
------------

First, please check the `issues on github <https://github.com/TDAmeritrade/stumpy/issues?utf8=%E2%9C%93&q=>`__ to see if your question has already been answered there. If no solution is available there feel free to open a new issue and the authors will attempt to respond in a reasonably timely fashion.

Alternatively, for general questions and comments, you can submit a post to the `STUMPY Discourse Group <https://stumpy.discourse.group/>`__.

------------
Contributing
------------

We welcome `contributions <https://github.com/TDAmeritrade/stumpy/blob/master/CONTRIBUTING.md>`__ in any form! Assistance with documentation, particularly expanding tutorials, is always welcome. To contribute please `fork the project <https://github.com/TDAmeritrade/stumpy/fork>`__, make your changes, and submit a pull request. We will do our best to work through any issues with you and get your code merged into the main branch.

------
Citing
------

If you have used this codebase in a scientific publication and wish to cite it, please use the `Journal of Open Source Software article <http://joss.theoj.org/papers/10.21105/joss.01504>`__.

    S. M. Law, *STUMPY: A Powerful and Scalable Python Library for Time Series Data Mining*
    In: Journal of Open Source Software, The Open Journal, Volume 4, Number 39.
    2019

.. code:: bibtex

    @article{law2017stumpy,
      title={{STUMPY: A Powerful and Scalable Python Library for Time Series Data Mining}},
      author={Law, Sean M.},
      journal={{The Journal of Open Source Software}},
      volume={4},
      number={39},
      pages={1504},
      year={2019}
    }

----------
References
----------

.. _publications:

Yeh, Chin-Chia Michael, et al. (2016) Matrix Profile I: All Pairs Similarity Joins for Time Series: A Unifying View that Includes Motifs, Discords, and Shapelets. ICDM:1317-1322. `Link <https://ieeexplore.ieee.org/abstract/document/7837992>`__

Zhu, Yan, et al. (2016) Matrix Profile II: Exploiting a Novel Algorithm and GPUs to Break the One Hundred Million Barrier for Time Series Motifs and Joins. ICDM:739-748. `Link <https://ieeexplore.ieee.org/abstract/document/7837898>`__

Yeh, Chin-Chia Michael, et al. (2017) Matrix Profile VI: Meaningful Multidimensional Motif Discovery. ICDM:565-574. `Link <https://ieeexplore.ieee.org/abstract/document/8215529>`__ 

Zhu, Yan, et al. (2017) Matrix Profile VII: Time Series Chains: A New Primitive for Time Series Data Mining. ICDM:695-704. `Link <https://ieeexplore.ieee.org/abstract/document/8215542>`__

Gharghabi, Shaghayegh, et al. (2017) Matrix Profile VIII: Domain Agnostic Online Semantic Segmentation at Superhuman Performance Levels. ICDM:117-126. `Link <https://ieeexplore.ieee.org/abstract/document/8215484>`__

-------------------
License & Trademark
-------------------

| STUMPY
| Copyright 2019 TD Ameritrade. Released under the terms of the 3-Clause BSD license.
| STUMPY is a trademark of TD Ameritrade IP Company, Inc. All rights reserved.
