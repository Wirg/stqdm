from stqdm.configuration_manager import ScopeManager


def test_scope_manager__get_default_config():
    scope_manager = ScopeManager({})
    assert scope_manager.get_default_config() == {}
    scope_manager = ScopeManager({"foo": "bar"})
    assert scope_manager.get_default_config() == {"foo": "bar"}


def test_scope_manager__set_default_config():
    scope_manager = ScopeManager({})
    assert scope_manager.get_default_config() == {}
    scope_manager.set_default_config({"foo": "bar"})
    assert scope_manager.get_default_config() == {"foo": "bar"}
    scope_manager.set_default_config({"foo": "baz", "bar": "foo"})
    assert scope_manager.get_default_config() == {"foo": "baz", "bar": "foo"}


def test_scope_manager__scope():
    scope_manager = ScopeManager({})
    assert scope_manager.get_current_scope_config() == {}
    with scope_manager.scope({"foo": "bar"}):
        assert scope_manager.get_current_scope_config() == {"foo": "bar"}
        with scope_manager.scope({"foo": "baz"}):
            assert scope_manager.get_current_scope_config() == {"foo": "baz"}
        assert scope_manager.get_current_scope_config() == {"foo": "bar"}
    assert scope_manager.get_current_scope_config() == {}


def test_scope_manager__use_current_default_if_config_not_provided():
    scope_manager = ScopeManager({"foo": "bar"})
    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar"}
    assert scope_manager.use_current_default_if_config_not_provided({"foo": "baz"}) == {"foo": "baz"}
    assert scope_manager.use_current_default_if_config_not_provided({"bar": "foo"}) == {"foo": "bar", "bar": "foo"}


def test_scope_manager__use_current_default_if_config_not_provided_with_scopes():
    scope_manager = ScopeManager({"foo": "bar"})
    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar"}
    with scope_manager.scope({"bar": "foo"}):
        assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar", "bar": "foo"}
        assert scope_manager.use_current_default_if_config_not_provided({"bar": "hello"}) == {"foo": "bar", "bar": "hello"}
        with scope_manager.scope({"bar": "baz"}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar", "bar": "baz"}
            assert scope_manager.use_current_default_if_config_not_provided({"bar": "hello"}) == {"foo": "bar", "bar": "hello"}
        assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar", "bar": "foo"}
    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar"}
