import pytest

from stqdm.configuration_manager import ScopeManager


def test_scope_manager__get_default_config():
    scope_manager = ScopeManager({})
    assert not scope_manager.get_default_config()
    scope_manager = ScopeManager({"foo": "bar"})
    assert scope_manager.get_default_config() == {"foo": "bar"}


def test_scope_manager__set_default_config():
    scope_manager = ScopeManager({})
    assert not scope_manager.get_default_config()
    scope_manager.set_default_config({"foo": "bar"})
    assert scope_manager.get_default_config() == {"foo": "bar"}
    scope_manager.set_default_config({"foo": "baz", "bar": "foo"})
    assert scope_manager.get_default_config() == {"foo": "baz", "bar": "foo"}


def test_scope_manager__set_default_config_rejects_non_mapping():
    scope_manager = ScopeManager({})

    with pytest.raises(TypeError, match="Config is not an instance of Mapping"):
        scope_manager.set_default_config(["not", "a", "mapping"])


def test_scope_manager__default_config_is_not_aliased_to_caller_mapping():
    default_config = {"foo": "initial"}
    scope_manager = ScopeManager(default_config)

    default_config["foo"] = "mutated"

    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "initial"}


def test_scope_manager__scope():
    scope_manager = ScopeManager({})
    assert not scope_manager.get_current_scope_config()
    with scope_manager.scope({"foo": "bar"}):
        assert scope_manager.get_current_scope_config() == {"foo": "bar"}
        with scope_manager.scope({"foo": "baz"}):
            assert scope_manager.get_current_scope_config() == {"foo": "baz"}
        assert scope_manager.get_current_scope_config() == {"foo": "bar"}
    assert not scope_manager.get_current_scope_config()


def test_scope_manager__scope_rejects_non_mapping():
    scope_manager = ScopeManager({})

    with pytest.raises(TypeError, match="Config is not an instance of Mapping"):
        with scope_manager.scope(["not", "a", "mapping"]):
            pass


def test_scope_manager__scope_config_is_not_aliased_to_caller_mapping():
    scope_config = {"foo": "initial"}
    scope_manager = ScopeManager({})

    with scope_manager.scope(scope_config):
        scope_config["foo"] = "mutated"

        assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "initial"}


def test_scope_manager__use_current_default_if_config_not_provided():
    scope_manager = ScopeManager({"foo": "bar"})
    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "bar"}
    assert scope_manager.use_current_default_if_config_not_provided({"foo": "baz"}) == {"foo": "baz"}
    assert scope_manager.use_current_default_if_config_not_provided({"bar": "foo"}) == {"foo": "bar", "bar": "foo"}


def test_scope_manager__provided_config_is_not_mutated():
    scope_manager = ScopeManager({"bar_format": "{desc}"})
    provided_config = {"desc": "direct"}

    with scope_manager.scope({"frontend": True}):
        assert scope_manager.use_current_default_if_config_not_provided(provided_config) == {
            "bar_format": "{desc}",
            "frontend": True,
            "desc": "direct",
        }

    assert provided_config == {"desc": "direct"}


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


def test_scope_manager__nested_scopes_inherit_outer_unset_values():
    scope_manager = ScopeManager({"foo": "default", "default_only": True})

    with scope_manager.scope({"foo": "outer", "bar": "outer"}):
        with scope_manager.scope({"bar": "inner"}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "foo": "outer",
                "bar": "inner",
                "default_only": True,
            }
            assert scope_manager.use_current_default_if_config_not_provided({"foo": "provided"}) == {
                "foo": "provided",
                "bar": "inner",
                "default_only": True,
            }


def test_scope_manager__empty_nested_scope_inherits_all_outer_values():
    scope_manager = ScopeManager({"frontend": True, "backend": False})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with scope_manager.scope({}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "frontend": True,
                "backend": False,
                "bar_format": "{desc}",
                "desc": "outer",
            }


def test_scope_manager__arbitrary_tqdm_kwargs_inherit_through_nested_scopes():
    scope_manager = ScopeManager({})

    with scope_manager.scope({"unit": "items", "dynamic_ncols": True}):
        with scope_manager.scope({"desc": "inner"}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "unit": "items",
                "dynamic_ncols": True,
                "desc": "inner",
            }


def test_scope_manager__inner_frontend_override_keeps_outer_format_values():
    scope_manager = ScopeManager({})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer", "frontend": True}):
        with scope_manager.scope({"frontend": False}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "bar_format": "{desc}",
                "desc": "outer",
                "frontend": False,
            }


def test_scope_manager__nested_scope_explicit_none_overrides_outer_value():
    scope_manager = ScopeManager({"frontend": True})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with scope_manager.scope({"bar_format": None}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "frontend": True,
                "bar_format": None,
                "desc": "outer",
            }


def test_scope_manager__nested_scope_empty_string_overrides_outer_value():
    scope_manager = ScopeManager({})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with scope_manager.scope({"bar_format": ""}):
            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "bar_format": "",
                "desc": "outer",
            }


def test_scope_manager__provided_none_overrides_nested_scope_value():
    scope_manager = ScopeManager({"bar_format": "{bar}"})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with scope_manager.scope({"desc": "inner"}):
            assert scope_manager.use_current_default_if_config_not_provided({"bar_format": None}) == {
                "bar_format": None,
                "desc": "inner",
            }


def test_scope_manager__three_nested_scopes_merge_from_outer_to_inner():
    scope_manager = ScopeManager({"frontend": True, "backend": False, "desc": "default"})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer", "leave": True}):
        with scope_manager.scope({"desc": "middle"}):
            with scope_manager.scope({"frontend": False}):
                assert scope_manager.use_current_default_if_config_not_provided({}) == {
                    "frontend": False,
                    "backend": False,
                    "bar_format": "{desc}",
                    "desc": "middle",
                    "leave": True,
                }


def test_scope_manager__three_nested_scopes_restore_one_level_at_a_time():
    scope_manager = ScopeManager({"desc": "default"})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with scope_manager.scope({"desc": "middle", "leave": True}):
            with scope_manager.scope({"frontend": False}):
                assert scope_manager.use_current_default_if_config_not_provided({}) == {
                    "bar_format": "{desc}",
                    "desc": "middle",
                    "leave": True,
                    "frontend": False,
                }

            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "bar_format": "{desc}",
                "desc": "middle",
                "leave": True,
            }

        assert scope_manager.use_current_default_if_config_not_provided({}) == {
            "bar_format": "{desc}",
            "desc": "outer",
        }

    assert scope_manager.use_current_default_if_config_not_provided({}) == {"desc": "default"}


def test_scope_manager__inner_exception_preserves_outer_scope_until_outer_exit():
    scope_manager = ScopeManager({"desc": "default"})

    with scope_manager.scope({"bar_format": "{desc}", "desc": "outer"}):
        with pytest.raises(RuntimeError, match="boom"):
            with scope_manager.scope({"desc": "inner"}):
                assert scope_manager.use_current_default_if_config_not_provided({}) == {
                    "bar_format": "{desc}",
                    "desc": "inner",
                }
                raise RuntimeError("boom")

        assert scope_manager.use_current_default_if_config_not_provided({}) == {
            "bar_format": "{desc}",
            "desc": "outer",
        }

    assert scope_manager.use_current_default_if_config_not_provided({}) == {"desc": "default"}


def test_scope_manager__mutating_outer_scope_mapping_does_not_change_inner_inheritance():
    outer_scope_config = {"bar_format": "{desc}", "desc": "outer"}
    scope_manager = ScopeManager({})

    with scope_manager.scope(outer_scope_config):
        with scope_manager.scope({"desc": "inner"}):
            outer_scope_config["bar_format"] = None

            assert scope_manager.use_current_default_if_config_not_provided({}) == {
                "bar_format": "{desc}",
                "desc": "inner",
            }


def test_scope_manager__mutating_middle_scope_mapping_does_not_change_inner_inheritance():
    middle_scope_config = {"bar_format": "{desc}", "desc": "middle"}
    scope_manager = ScopeManager({"frontend": True})

    with scope_manager.scope({"desc": "outer"}):
        with scope_manager.scope(middle_scope_config):
            with scope_manager.scope({"frontend": False}):
                middle_scope_config["bar_format"] = ""

                assert scope_manager.use_current_default_if_config_not_provided({}) == {
                    "frontend": False,
                    "bar_format": "{desc}",
                    "desc": "middle",
                }


def test_scope_manager__scope_restores_previous_context_after_exception():
    scope_manager = ScopeManager({"foo": "default"})

    try:
        with scope_manager.scope({"foo": "outer", "bar": "outer"}):
            with scope_manager.scope({"foo": "inner"}):
                assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "inner", "bar": "outer"}
                raise RuntimeError("boom")
    except RuntimeError:
        pass

    assert scope_manager.use_current_default_if_config_not_provided({}) == {"foo": "default"}
