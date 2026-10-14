"""Group ads into products by advertiser page + landing domain."""
from urllib.parse import urlparse

from finder.models import Ad, Product


def normalize_domain(url: str) -> str:
    """'https://WWW.Shop.com/x' -> 'shop.com'. Also accepts bare domains like 'SHOP.COM'."""
    url = url.strip().lower()
    if "://" not in url:
        url = "http://" + url
    host = urlparse(url).hostname or ""
    return host.removeprefix("www.")


def group_ads(ads: list[Ad]) -> list[Product]:
    products: dict[tuple[str, str], Product] = {}
    for ad in ads:
        domain = normalize_domain(ad.landing_url)
        key = (ad.page_id, domain)
        if key not in products:
            products[key] = Product(page_id=ad.page_id, page_name=ad.page_name, domain=domain)
        products[key].ads.append(ad)
    return list(products.values())
