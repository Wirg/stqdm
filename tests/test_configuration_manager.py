import pytest

from stqdm.configuration_manager import ScopeError, ScopeManager


def test_scope_manager__get_current_defaults():
    scope_manager = ScopeManager([{}])
    assert scope_manager.get_current_defaults() == {}
    scope_manager = ScopeManager([{"foo": "bar"}])
    assert scope_manager.get_current_defaults() == {"foo": "bar"}


def test_scope_manager__set_default_kwargs():
    scope_manager = ScopeManager([{}])
    assert scope_manager.get_current_defaults() == {}
    scope_manager.set_default_kwargs({"foo": "bar"})
    assert scope_manager.get_current_defaults() == {"foo": "bar"}
    scope_manager.set_default_kwargs({"foo": "baz", "bar": "foo"})
    assert scope_manager.get_current_defaults() == {"foo": "baz", "bar": "foo"}


def test_scope_manager__use_current_default_if_config_not_provided():
    scope_manager = ScopeManager([{"foo": "bar"}])
    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar"}
    assert scope_manager.use_current_default_if_config_not_provided({"foo": "baz"}) == {"foo": "baz"}
    assert scope_manager.use_current_default_if_config_not_provided({"bar": "foo"}) == {"foo": "bar", "bar": "foo"}


def test_scope_manager__scope():
    scope_manager = ScopeManager([{}])
    assert scope_manager.get_current_defaults() == {}
    with scope_manager.scope({"foo": "bar"}):
        assert scope_manager.get_current_defaults() == {"foo": "bar"}
        with scope_manager.scope({"foo": "baz"}):
            assert scope_manager.get_current_defaults() == {"foo": "baz"}
        assert scope_manager.get_current_defaults() == {"foo": "bar"}
    assert scope_manager.get_current_defaults() == {}


def test_configuration_manager__raise_for_access_to_non_existing_default():
    scope_manager = ScopeManager()
    with pytest.raises(ScopeError):
        scope_manager.get_current_defaults()
    with pytest.raises(ScopeError):
        scope_manager.use_current_default_if_config_not_provided({})
