"""Flask Test Environment Configuration."""

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class TestConfig(DefaultConfig):
    # LRU cache settings
    LRU_CACHE_TIME = 300  # in seconds
