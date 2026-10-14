"""Central settings: markets, score weights and thresholds."""

# Countries where we already sell. A product with reach here is "present".
TARGET_MARKETS = ["SI", "HR", "HU", "PL", "SK", "CZ", "RO", "GR", "BG", "IT", "DE"]

DEFAULT_SOURCE_COUNTRIES = ["FR", "ES", "NL", "AT"]

# Our product categories: t-shirts, men's boxers/underwear and socks.
# Used when no --keywords are given.
DEFAULT_KEYWORDS = ["boxers", "briefs", "underwear", "socks", "t-shirt", "undershirt"]

# Score weights (sum = 100). Components that return None are skipped and the
# total is rescaled over the remaining weights.
WEIGHTS = {
    "ad_age": 30,
    "new_creatives": 20,
    "active_ads": 15,
    "eu_reach": 15,
    "reviews": 10,   # placeholder
    "traffic": 10,   # placeholder
}

# Ad age: (days, score) points, linearly interpolated between them.
AD_AGE_CURVE = [(7, 0.0), (30, 0.5), (60, 0.8), (90, 1.0)]

NEW_CREATIVE_WINDOW_DAYS = 30
NEW_CREATIVES_FOR_MAX = 10
ACTIVE_ADS_FOR_MAX = 30
# EU reach is scored on a log scale between these two values.
EU_REACH_FOR_ZERO = 1_000
EU_REACH_FOR_MAX = 1_000_000
