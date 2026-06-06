from abc import ABCMeta
from contextlib import contextmanager
from typing import Any, Generator, Mapping

ConfigMapping = Mapping[str, Any]
Config = dict[str, Any]


class ScopeManager(metaclass=ABCMeta):  # pylint: disable=invalid-name
    """A Manager for handling scoped configurations with a stack to maintain context states.

    This helps handling `scope` context manager and has a default configuration (specific level-0 scope).
    This is a generic class made to handle `Mapping`s. Those will be tqdm + stqdm configurations parameters.

    Attributes:
        default_config (Config): The default configuration. This is a specific scope (level-0 scope).
            By default, it does not behave in the same way as other scope.
            It's argument are kept unless overridden by the latest scope in the stack.
        _scope_stack (list[Config]): A list that tracks all active scope configurations.
    """

    def __init__(self, default_config: ConfigMapping) -> None:
        """Initializes the ScopeManager with a default configuration.

        Args:
            default_config (ConfigMapping): The default configuration dictionary.

        Raises:
            TypeError: If the default_config is not an instance of Mapping.
        """
        self._default_config = self._copy_config(default_config)
        self._scope_stack: list[Config] = []

    @staticmethod
    def _copy_config(config: ConfigMapping) -> Config:
        if not isinstance(config, Mapping):
            raise TypeError("Config is not an instance of Mapping.")
        return dict(config)

    @property
    def default_config(self) -> Config:
        return self.get_default_config()

    @default_config.setter
    def default_config(self, default_config: ConfigMapping) -> None:
        self.set_default_config(default_config)

    def set_default_config(self, default_config: ConfigMapping) -> None:
        """Sets the default configuration of the ScopeManager.

        Args:
            default_config (ConfigMapping): The configuration to set as default.
        """
        self._default_config = self._copy_config(default_config)

    def get_default_config(self) -> Config:
        """Retrieves the current default configuration.

        Returns:
            Config: The default configuration.
        """
        return dict(self._default_config)

    @contextmanager
    def scope(self, scope_config: ConfigMapping) -> Generator[Config, None, None]:
        """A context manager that temporarily adds a new configuration to the stack.

        Args:
            scope_config (ConfigMapping): The temporary configuration for the scope.

        Yields:
            Config: The provided configuration.
        """
        scope_snapshot = self._copy_config(scope_config)
        self._scope_stack.append(scope_snapshot)
        try:
            yield dict(scope_snapshot)
        finally:
            self._scope_stack.pop()

    def get_current_scope_config(self) -> Config:
        """Retrieves the configuration of the current scope.

        Returns:
            Config: The active scope configuration if any, otherwise an empty dictionary.
        """
        if self._scope_stack:
            return dict(self._scope_stack[-1])
        return {}

    def use_current_default_if_config_not_provided(self, config: ConfigMapping) -> Config:
        """Merges the provided configuration with the defaults and active scope configurations.

        This is the logic that implements the default merge for configurations.
        The new config is the latest provided values in order:
        - default_config (less important)
        - active scopes, from outermost to innermost
        - current_config (stqdm call params) (most important)

        Args:
            config (ConfigMapping): The configuration to merge with defaults and current scope.

        Returns:
            Config: The resulting configuration after merging.
        """
        merged_config = dict(self._default_config)
        for scope_config in self._scope_stack:
            merged_config.update(scope_config)
        merged_config.update(config)
        return merged_config
