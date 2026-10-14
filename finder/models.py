from dataclasses import dataclass, field
from datetime import date


@dataclass
class Ad:
    ad_id: str
    page_id: str
    page_name: str
    start_date: date
    landing_url: str
    body: str = ""
    snapshot_url: str = ""
    reach_by_country: dict[str, int] = field(default_factory=dict)


@dataclass
class Product:
    page_id: str
    page_name: str
    domain: str
    ads: list[Ad] = field(default_factory=list)

    # Filled in by scoring.score_product
    oldest_ad_days: int = 0
    new_ads_30d: int = 0
    active_ads: int = 0
    eu_reach: int = 0
    present_in_markets: list[str] = field(default_factory=list)
    components: dict[str, float | None] = field(default_factory=dict)
    score: float = 0.0

    @property
    def in_our_markets(self) -> bool:
        return bool(self.present_in_markets)
