"""
Pytest yapılandırması ve paylaşılan fixture'lar.
"""
import pytest
from src.models import VillageData, ResourceTotals, ThresholdConfig, AppState


@pytest.fixture
def sample_village():
    return VillageData(name="Köy 1", wood=1000, clay=2000, iron=1500, food=500)


@pytest.fixture
def sample_villages():
    return [
        VillageData(name="Köy 1", wood=1000, clay=2000, iron=1500, food=500),
        VillageData(name="Köy 2", wood=3000, clay=1000, iron=2500, food=1500),
        VillageData(name="Köy 3", wood=500,  clay=750,  iron=250,  food=100),
    ]


@pytest.fixture
def empty_totals():
    return ResourceTotals()


@pytest.fixture
def default_threshold_config():
    return ThresholdConfig()


@pytest.fixture
def default_app_state():
    return AppState()
