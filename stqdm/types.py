from typing import TYPE_CHECKING, Any, Mapping, Optional

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


class STQDMArgs(TypedDict, total=False):
    desc: Optional[str]
    total: Optional[float]
    leave: Optional[bool]
    ncols: Optional[int]
    mininterval: float
    maxinterval: float
    miniters: Optional[float]
    ascii: bool | str | None
    disable: Optional[bool]
    unit: str
    unit_scale: bool | float
    dynamic_ncols: bool
    smoothing: float
    bar_format: Optional[str]
    initial: float
    position: Optional[int]
    postfix: Mapping[str, object] | str | None
    unit_divisor: float
    write_bytes: bool
    lock_args: tuple[Optional[bool], Optional[float]] | tuple[Optional[bool]] | None
    nrows: Optional[int]
    colour: Optional[str]
    delay: Optional[float]
    gui: bool
    file: Any
    frontend: bool
    backend: bool
    st_container: "DeltaGenerator"
