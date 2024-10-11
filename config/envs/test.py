"""Flask Test Environment Configuration."""
from os import environ

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class TestConfig(DefaultConfig):
    # LRU cache settings
    LRU_CACHE_TIME = 300  # in seconds
