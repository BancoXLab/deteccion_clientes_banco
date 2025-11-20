import os
import requests
import logging

logger = logging.getLogger(__name__)

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK_URL")
ALERTS_EMAIL = os.getenv("ALERTS_EMAIL")

def notify_slack(text: str):
    if not SLACK_WEBHOOK:
        logger.debug("No SLACK_WEBHOOK_URL configured, skipping slack notify")
        return False
    try:
        resp = requests.post(SLACK_WEBHOOK, json={"text": text}, timeout=5)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.exception("Failed to send Slack notification: %s", e)
        return False

def notify_email(subject: str, body: str):
    # Simple placeholder: in production use sendgrid/mailgun or SMTP with retries
    if not ALERTS_EMAIL:
        logger.debug("No ALERTS_EMAIL configured, skipping email notify")
        return False
    try:
        # send via a transactional provider or SMTP - left as a placeholder
        logger.info("Would send email to %s: %s", ALERTS_EMAIL, subject)
        return True
    except Exception as e:
        logger.exception("Failed to send email: %s", e)
        return False
