import logging

from pytrends.request import TrendReq

logger = logging.getLogger(__name__)


def get_trending_queries(topic: str, max_results: int = 10) -> list[str]:
    """
    Free trending-keyword signal from Google Trends (unofficial API, no key needed).
    Returns rising + top related queries for the topic -- i.e. what people are
    actually searching for around this topic right now. Best-effort: Google Trends'
    unofficial API is occasionally flaky/rate-limited, so this returns [] on failure
    instead of breaking the pipeline.
    """
    if not topic:
        return []
    try:
        pytrends = TrendReq(hl="en-US", tz=0)
        pytrends.build_payload([topic], timeframe="now 7-d")
        related = pytrends.related_queries()
        data = related.get(topic) or {}

        results: list[str] = []
        for key in ("rising", "top"):
            df = data.get(key)
            if df is not None and not df.empty:
                results.extend(df["query"].tolist())

        seen = set()
        unique: list[str] = []
        for r in results:
            key = r.lower()
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique[:max_results]
    except Exception as e:
        logger.warning(f"Google Trends lookup failed for '{topic}': {e}")
        return []
