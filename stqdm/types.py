from typing import TYPE_CHECKING, Optional

from typing_extensions import TypedDict

if TYPE_CHECKING:
    from streamlit.delta_generator import DeltaGenerator


class STQDMArgs(TypedDict, total=False):
    desc: str
    leave: bool
    ncols: Optional[int]
    disable: bool
    bar_format: Optional[str]
    delay: float
    frontend: bool
    backend: bool
    st_container: "DeltaGenerator"
