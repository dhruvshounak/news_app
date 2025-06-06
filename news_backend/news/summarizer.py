from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging

logger = logging.getLogger(__name__)

try:
    tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
    model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
except Exception as e:
    logger.error(f"Failed to load DistilBART: {e}")
    raise

def summarize_text(text, max_length=130, min_length=30):
    if not text or len(text.strip()) < 50:
        logger.warning("Text too short or empty.")
        return "Text too short or empty to summarize."
    try:
        text = text[:2000]  # Truncate for memory
        inputs = tokenizer([text], max_length=1024, return_tensors="pt", truncation=True)
        summary_ids = model.generate(
            inputs['input_ids'],
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            early_stopping=True
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        logger.info(f"Generated summary: {summary[:50]}...")
        return summary
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return "Failed to generate summary."