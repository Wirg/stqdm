from abc import ABCMeta
from contextlib import contextmanager
from typing import Any, Generic, Iterator, List, Mapping, TypeVar, cast

ScopeConfig = TypeVar("ScopeConfig", bound=Mapping[str, Any])


class ScopeManager(Generic[ScopeConfig], metaclass=ABCMeta):  # pylint: disable=invalid-name,inconsistent-mro
    """A Manager for handling scoped configurations `ScopeConfig` with a stack to maintain context states.

    This helps handling `scope` context manager and has a default configuration (specific level-0 scope).
    This is a generic class made to handle `Mapping`s. Those will be tqdm + stqdm configurations parameters.

    Attributes:
        default_config (ScopeConfig): The default configuration. This is a specific scope (level-0 scope).
            By default, it does not behave in the same way as other scope.
            It's argument are kept unless overridden by the latest scope in the stack.
        _scope_stack (List[ScopeConfig]): A list that tracks all active scope configurations.
    """

    def __init__(self, default_config: ScopeConfig) -> None:
        """Initializes the ScopeManager with a default configuration.

        Args:
            default_config (ScopeConfig): The default configuration dictionary.

        Raises:
            TypeError: If the default_config is not an instance of Mapping.
        """
        if not isinstance(default_config, Mapping):
            raise TypeError("Default config is not an instance of Mapping.")
        self.default_config: ScopeConfig = default_config
        self._scope_stack: List[ScopeConfig] = []

    def set_default_config(self, default_config: ScopeConfig) -> None:
        """Sets the default configuration of the ScopeManager.

        Args:
            default_config (ScopeConfig): The configuration to set as default.
        """
        self.default_config = default_config

    def get_default_config(self) -> ScopeConfig:
        """Retrieves the current default configuration.

        Returns:
            ScopeConfig: The default configuration.
        """
        return self.default_config

    @contextmanager
    def scope(self, scope_config: ScopeConfig) -> Iterator[ScopeConfig]:
        """A context manager that temporarily adds a new configuration to the stack.

        Args:
            scope_config (ScopeConfig): The temporary configuration for the scope.

        Yields:
            ScopeConfig: The provided configuration.
        """
        self._scope_stack.append(scope_config)
        try:
            yield scope_config
        finally:
            self._scope_stack.pop()

    def get_current_scope_config(self) -> ScopeConfig:
        """Retrieves the configuration of the current scope.

        Returns:
            ScopeConfig: The active scope configuration if any, otherwise an empty dictionary.
        """
        if self._scope_stack:
            return self._scope_stack[-1]
        return {}

    def use_current_default_if_config_not_provided(self, config: ScopeConfig) -> ScopeConfig:
        """Merges the provided configuration with the defaults and the current scope configuration.

        This is the logic that implements the default merge for configurations.
        The new config is the latest provided values in order:
        - default_config (less important)
        - latest scope
        - current_config (stqdm call params) (most important)
        It ignores all the intermediary scopes.

        Args:
            config (ScopeConfig): The configuration to merge with defaults and current scope.

        Returns:
            ScopeConfig: The resulting configuration after merging.
        """
        # This typing is probably wrong, but in our case, we will be using a TypedDict and it should be ok
        return cast(ScopeConfig, {**self.get_default_config(), **self.get_current_scope_config(), **config})
