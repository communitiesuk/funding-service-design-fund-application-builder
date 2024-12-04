"""Flask configuration."""

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UatConfig(DefaultConfig):
    GENERATE_LOCAL_CONFIG = True
