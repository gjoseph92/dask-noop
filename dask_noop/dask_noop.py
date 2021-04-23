from typing import Mapping, Union

import dask
from dask.blockwise import Blockwise
from dask.core import istask
from dask.delayed import Delayed
from dask.highlevelgraph import Layer, MaterializedLayer


def noop(*args, **kwargs):
    pass


def subs_noop(task):
    if istask(task):
        return (noop,) + tuple(subs_noop(arg) for arg in task[1:])
    else:
        if type(task) is list:
            return [subs_noop(x) for x in task]
        return task


def rewrite_noop_dsk(dsk: Mapping) -> dict:
    return {k: subs_noop(task) for k, task in dsk.items()}


def rewrite_noop_blockwise(blockwise: Blockwise) -> Blockwise:
    lyr = Blockwise(
        blockwise.output,
        blockwise.output_indices,
        rewrite_noop_dsk(blockwise.dsk),
        blockwise.indices,
        blockwise.numblocks,
        blockwise.concatenate,
        blockwise.new_axes,
        blockwise.output_blocks,
        blockwise.annotations,
        blockwise.io_deps,
    )
    if lyr.concatenate:
        # We don't want `concatenate_axes` inserted into the graph, but we also don't want
        # `optimize_blockwise` to fuse layers that couldn't be fused in the original graph because
        # their `concatenate` settings didn't match. So we use a falsey value that shouldn't be equal
        # to the `concatenate` setting for other layers.
        lyr.concatenate = 0  # type: ignore
    return lyr


def rewrite_noop_layer(layer: Layer) -> Union[Blockwise, MaterializedLayer]:
    if isinstance(layer, Blockwise):
        return rewrite_noop_blockwise(layer)
    return MaterializedLayer(rewrite_noop_dsk(layer), annotations=layer.annotations)


def as_noop(obj) -> Delayed:
    """
    Delayed with the same graph structure as ``obj``, where every operation is replaced with a no-op.
    """
    d = dask.delayed(obj)
    d._dask.layers = {k: rewrite_noop_layer(lyr) for k, lyr in d._dask.layers.items()}

    return d
