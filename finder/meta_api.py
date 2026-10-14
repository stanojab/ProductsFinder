"""Meta Ad Library API client. NOT IMPLEMENTED YET (waiting for API access).

Plan (to verify against the current docs before implementing):
  Endpoint: GET https://graph.facebook.com/<version>/ads_archive
  Params:   access_token, search_terms, ad_reached_countries=[...], ad_active_status=ACTIVE,
            ad_type=ALL, limit, fields=...
  Fields:   id, page_id, page_name, ad_delivery_start_time, ad_creative_bodies,
            ad_creative_link_captions (landing domain), ad_snapshot_url,
            eu_total_reach, age_country_gender_reach_breakdown (reach per country),
            target_locations
  Paging:   follow paging.next; back off on rate-limit errors (code 4 / 17 / 613)
            and watch the X-Business-Use-Case-Usage header.
  Caching:  store every fetched ad with finder.cache.save_ads, keyed by ad id.

The function must return list[finder.models.Ad]; everything downstream already works on that.
"""
from finder.models import Ad


def fetch_ads(keywords: list[str], countries: list[str], token: str) -> list[Ad]:
    raise NotImplementedError(
        "Live Meta Ad Library mode is not implemented yet. Run with --demo to see the tool working."
    )
