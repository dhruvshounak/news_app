from celery import shared_task
from news.models import NewsArticle
from news.summarizer import summarize_text
import logging

logger = logging.getLogger(__name__)

@shared_task
def summarize_article(article_id):
    try:
        article = NewsArticle.objects.get(id=article_id)
        if article.summary:
            logger.info(f"Article {article.title} already summarized.")
            return f"Article {article.title} already summarized."
        text_to_summarize = article.full_content or article.content or ""
        if not text_to_summarize:
            logger.warning(f"No content to summarize for article {article.title}.")
            return f"No content to summarize for article {article.title}."
        summary = summarize_text(text_to_summarize)
        article.summary = summary
        article.save()
        logger.info(f"Summarized article {article.title}: {summary[:50]}...")
        return f"Summarized article {article.title}: {summary[:50]}..."
    except NewsArticle.DoesNotExist:
        logger.error(f"Article with ID {article_id} not found.")
        return f"Article with ID {article_id} not found."
    except Exception as e:
        logger.error(f"Failed to summarize article {article_id}: {e}")
        return f"Error summarizing article {article_id}: {e}"