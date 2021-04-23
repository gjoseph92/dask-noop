# dask-noop

Turn any dask collection into a [dask.delayed](https://docs.dask.org/en/latest/delayed.html), where all the functions in its graph are replaced with no-ops.

Useful for benchmarking how much the graph structure itself is affecting performance.

## Example

```python
from dask.diagnostics import ProgressBar
import dask.array as da
from dask_noop import as_noop

arr = da.random.random((100, 2_000, 3_000), chunks=(10, 100, 100))
delta = da.diff(arr, n=5)
positive = delta[delta > 0]
x = positive.mean()

x_noop = as_noop(x)
```

This relatively simple task is more compute-bound:
```python
In [5]: with ProgressBar():
   ...:     arr.mean().compute()
   ...:
[########################################] | 100% Completed |  3.2s

In [6]: with ProgressBar():
   ...:     as_noop(arr.mean()).compute()
   ...:
[########################################] | 100% Completed |  0.9s
```

This complex graph suffers from high task overhead:
```python
In [3]: with ProgressBar():
   ...:     x.compute()
   ...:
[########################################] | 100% Completed |  1min 14.5s

In [4]: with ProgressBar():
   ...:     x_noop.compute()
   ...:
[########################################] | 100% Completed | 59.5s
```

## Installation

```
pip install git+https://github.com/gjoseph92/dask-noop.git
```
