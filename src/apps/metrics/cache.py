from django.core.cache import cache

RECORDS_CACHE_TIMEOUT = 60 * 5


def get_records_cache_key(metric_id: int) -> str:
    return f"metric_records_list_{metric_id}"


def cache_records(metric_id: int, data: object) -> None:
    key = get_records_cache_key(metric_id)
    cache.set(key, data, timeout=RECORDS_CACHE_TIMEOUT)


def get_cached_records(metric_id: int) -> object | None:
    key = get_records_cache_key(metric_id)
    return cache.get(key)


def invalidate_records_cache(metric_id: int) -> None:
    key = get_records_cache_key(metric_id)
    cache.delete(key)
