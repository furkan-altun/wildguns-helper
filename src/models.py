from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VillageData:
    name: str
    wood: int
    clay: int
    iron: int
    food: int


@dataclass
class ResourceTotals:
    wood: int = 0
    clay: int = 0
    iron: int = 0
    food: int = 0


@dataclass
class ThresholdConfig:
    wood: int | None = None    # None = devre dışı
    clay: int | None = None
    iron: int | None = None
    food: int | None = None


@dataclass
class AppState:
    villages: list[VillageData] = field(default_factory=list)
    totals: ResourceTotals = field(default_factory=ResourceTotals)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    last_updated: datetime | None = None
    is_running: bool = False
    silenced_resources: set[str] = field(default_factory=set)
