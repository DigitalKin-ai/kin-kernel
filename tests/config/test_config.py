from kinkernel.config.base import ConfigModel, EnvVar
import pytest


# Test creating a ConfigModel with no env_vars provided
def test_config_model_empty():
    config = ConfigModel()
    assert config.env_vars == []


# Test creating a ConfigModel with env_vars provided
def test_config_model_with_env_vars():
    env_vars = [EnvVar(key="KEY1", value="VALUE1"), EnvVar(key="KEY2", value="VALUE2")]
    config = ConfigModel(env_vars=env_vars)
    assert len(config.env_vars) == 2
    assert config.env_vars[0].key == "KEY1"
    assert config.env_vars[0].value == "VALUE1"
    assert config.env_vars[1].key == "KEY2"
    assert config.env_vars[1].value == "VALUE2"


# Test creating EnvVar objects
@pytest.mark.parametrize(
    "key, value",
    [
        ("DATABASE_URL", "postgres://user:pass@localhost/dbname"),
        ("SECRET_KEY", "supersecretkey"),
    ],
)
def test_env_var(key, value):
    env_var = EnvVar(key=key, value=value)
    assert env_var.key == key
    assert env_var.value == value
