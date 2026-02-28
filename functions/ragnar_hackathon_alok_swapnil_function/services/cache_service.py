import json
import logging

logger = logging.getLogger(__name__)

QUEUE_CACHE_PREFIX = "queue_"
STATS_CACHE_PREFIX = "stats_"


def get_cache_segment(app):
    """Get the default cache segment."""
    return app.cache().segment()


def set_queue_state(app, clinic_id, queue_data):
    """Cache the live queue state for a clinic."""
    try:
        segment = get_cache_segment(app)
        key = f"{QUEUE_CACHE_PREFIX}{clinic_id}"
        segment.put(key, json.dumps(queue_data))
        return True
    except Exception as e:
        logger.error(f"Failed to cache queue state: {e}")
        return False


def get_queue_state(app, clinic_id):
    """Get cached queue state for a clinic."""
    try:
        segment = get_cache_segment(app)
        key = f"{QUEUE_CACHE_PREFIX}{clinic_id}"
        result = segment.get(key)
        if result and result.get("cache_value"):
            return json.loads(result["cache_value"])
        return None
    except Exception as e:
        logger.error(f"Failed to get cached queue state: {e}")
        return None


def set_dashboard_stats(app, clinic_id, stats_data):
    """Cache dashboard statistics for fast loading."""
    try:
        segment = get_cache_segment(app)
        key = f"{STATS_CACHE_PREFIX}{clinic_id}"
        segment.put(key, json.dumps(stats_data))
        return True
    except Exception as e:
        logger.error(f"Failed to cache dashboard stats: {e}")
        return False


def get_dashboard_stats(app, clinic_id):
    """Get cached dashboard statistics."""
    try:
        segment = get_cache_segment(app)
        key = f"{STATS_CACHE_PREFIX}{clinic_id}"
        result = segment.get(key)
        if result and result.get("cache_value"):
            return json.loads(result["cache_value"])
        return None
    except Exception as e:
        logger.error(f"Failed to get cached stats: {e}")
        return None
