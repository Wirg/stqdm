from abc import ABCMeta
from contextlib import contextmanager
from typing import Any, Generic, Iterator, List, Mapping, Optional, TypeVar, cast


class ScopeError(RuntimeError):
    pass


ScopeConfig = TypeVar("ScopeConfig", bound=Mapping[str, Any])


class ScopeManager(Generic[ScopeConfig], metaclass=ABCMeta):  # pylint: disable=invalid-name,inconsistent-mro
    def __init__(self, stack: Optional[List[ScopeConfig]] = None) -> None:
        if stack is None:
            stack = []
        self._scope_stack: List[ScopeConfig] = stack

    def set_default_kwargs(self, scope_config: ScopeConfig) -> None:
        if not self._scope_stack:
            self._scope_stack.append(scope_config)
        else:
            self._scope_stack[0] = scope_config

    @contextmanager
    def scope(self, scope_config: ScopeConfig) -> Iterator[ScopeConfig]:
        self._scope_stack.append(scope_config)
        try:
            yield scope_config
        finally:
            self._scope_stack.pop()

    def get_current_defaults(self) -> ScopeConfig:
        if self._scope_stack:
            return self._scope_stack[-1]
        raise ScopeError("No default scope set. You may have messed up with the scope stack. Please report this issue.")

    def use_current_default_if_config_not_provided(self, config: ScopeConfig) -> ScopeConfig:
        # This typing is probably wrong, but in our case, we will be using a TypedDict and it should be ok
        return cast(ScopeConfig, {**self.get_current_defaults(), **config})
