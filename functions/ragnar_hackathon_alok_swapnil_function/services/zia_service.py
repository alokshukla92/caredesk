import logging

logger = logging.getLogger(__name__)


def analyze_sentiment(app, text):
    """
    Analyze sentiment of text using Zia Text Analytics.
    Returns: "positive", "negative", or "neutral"
    """
    if not text or not text.strip():
        return "neutral"

    try:
        zia = app.zia()
        result = zia.get_sentiment_analysis(text)
        sentiment = result.get("sentiment", "neutral").lower()
        logger.info(f"Sentiment for text: {sentiment}")
        return sentiment
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "neutral"


def extract_keywords(app, text):
    """
    Extract keywords from text using Zia Text Analytics.
    Returns list of keywords.
    """
    if not text or not text.strip():
        return []

    try:
        zia = app.zia()
        result = zia.get_keyword_extraction(text)
        keywords = [item.get("keyword", "") for item in result if item.get("keyword")]
        logger.info(f"Extracted keywords: {keywords}")
        return keywords
    except Exception as e:
        logger.error(f"Keyword extraction failed: {e}")
        return []


def perform_ocr(app, file_path):
    """
    Perform OCR on an image file using Zia.
    Returns extracted text.
    """
    try:
        zia = app.zia()
        result = zia.extract_optical_characters(file_path)
        text = result.get("text", "")
        logger.info(f"OCR extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""
