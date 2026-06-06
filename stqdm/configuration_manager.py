from contextlib import contextmanager
from typing import Any, Generic, Iterator, Mapping, TypeVar, cast

Config = TypeVar("Config", bound=Mapping[str, Any])


class ScopeManager(Generic[Config]):
    """A Manager for handling scoped configurations with a stack to maintain context states.

    This helps handling `scope` context manager and has a default configuration (specific level-0 scope).
    This is a generic class made to handle `Mapping`s. Those will be tqdm + stqdm configurations parameters.

    Attributes:
        default_config (Config): The default configuration. This is a specific scope (level-0 scope).
            By default, it does not behave in the same way as other scope.
            It's argument are kept unless overridden by the latest scope in the stack.
        _scope_stack (list[Config]): A list that tracks all active scope configurations.
    """

    def __init__(self, default_config: Config) -> None:
        """Initializes the ScopeManager with a default configuration.

        Args:
            default_config (Config): The default configuration dictionary.

        Raises:
            TypeError: If the default_config is not an instance of Mapping.
        """
        if not isinstance(default_config, Mapping):
            raise TypeError("Config is not an instance of Mapping.")
        self._default_config = cast(Config, dict(default_config))
        self._scope_stack: list[Config] = []

    def set_default_config(self, default_config: Config) -> None:
        """Sets the default configuration of the ScopeManager.

        Args:
            default_config (Config): The configuration to set as default.
        """
        if not isinstance(default_config, Mapping):
            raise TypeError("Config is not an instance of Mapping.")
        self._default_config = cast(Config, dict(default_config))

    def get_default_config(self) -> Config:
        """Retrieves the current default configuration.

        Returns:
            Config: The default configuration.
        """
        return self._default_config

    @contextmanager
    def scope(self, scope_config: Config) -> Iterator[Config]:
        """A context manager that temporarily adds a new configuration to the stack.

        Args:
            scope_config (Config): The temporary configuration for the scope.

        Yields:
            Config: The provided configuration.
        """
        if not isinstance(scope_config, Mapping):
            raise TypeError("Config is not an instance of Mapping.")
        scope_snapshot = cast(Config, dict(scope_config))
        self._scope_stack.append(scope_snapshot)
        try:
            yield scope_snapshot
        finally:
            self._scope_stack.pop()

    def get_current_scope_config(self) -> Config:
        """Retrieves the configuration of the current scope.

        Returns:
            Config: The active scope configuration if any, otherwise an empty dictionary.
        """
        if self._scope_stack:
            return self._scope_stack[-1]
        return cast(Config, {})

    def use_current_default_if_config_not_provided(self, config: Config) -> Config:
        """Merges the provided configuration with the defaults and active scope configurations.

        This is the logic that implements the default merge for configurations.
        The new config is the latest provided values in order:
        - default_config (less important)
        - active scopes, from outermost to innermost
        - current_config (stqdm call params) (most important)

        Args:
            config (Config): The configuration to merge with defaults and current scope.

        Returns:
            Config: The resulting configuration after merging.
        """
        merged_config = dict(self._default_config)
        for scope_config in self._scope_stack:
            merged_config.update(scope_config)
        merged_config.update(config)
        return cast(Config, merged_config)
