from __future__ import annotations

from pydantic import BaseModel

from core.steps import registry


def test_every_action_follows_the_contract() -> None:
    modules = registry.actions()
    assert modules, "至少应该注册一个动作"
    for name, module in modules.items():
        assert module.ACTION == name
        assert isinstance(module.LABEL, str) and module.LABEL
        assert isinstance(module.RETRY_SAFE, bool)
        assert issubclass(module.Params, BaseModel)
        assert module.Params.model_config.get("extra") == "forbid"
        assert callable(module.run)


def test_action_names_are_unique() -> None:
    actions = registry.actions()
    assert len(actions) == len(set(actions))
