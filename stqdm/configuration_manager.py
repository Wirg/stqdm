from abc import ABCMeta
from contextlib import contextmanager
from typing import Any, Generic, Iterator, List, Mapping, TypeVar, cast

ScopeConfig = TypeVar("ScopeConfig", bound=Mapping[str, Any])


class ScopeManager(Generic[ScopeConfig], metaclass=ABCMeta):  # pylint: disable=invalid-name,inconsistent-mro
    def __init__(self, default_config: ScopeConfig) -> None:
        if not isinstance(default_config, Mapping):
            raise TypeError("Default config is not an instance of Mapping.")
        self.default_config: ScopeConfig = default_config
        self._scope_stack: List[ScopeConfig] = []

    def set_default_config(self, default_config: ScopeConfig) -> None:
        self.default_config = default_config

    def get_default_config(self) -> ScopeConfig:
        return self.default_config

    @contextmanager
    def scope(self, scope_config: ScopeConfig) -> Iterator[ScopeConfig]:
        self._scope_stack.append(scope_config)
        try:
            yield scope_config
        finally:
            self._scope_stack.pop()

    def get_current_scope_config(self) -> ScopeConfig:
        if self._scope_stack:
            return self._scope_stack[-1]
        return {}

    def use_current_default_if_config_not_provided(self, config: ScopeConfig) -> ScopeConfig:
        # This typing is probably wrong, but in our case, we will be using a TypedDict and it should be ok
        return cast(ScopeConfig, {**self.get_default_config(), **self.get_current_scope_config(), **config})
