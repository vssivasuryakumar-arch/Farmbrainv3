"""SMTP email delivery. Gmail SMTP works with a Google App Password."""
from email.message import EmailMessage
import smtplib
import ssl

from flask import current_app


def send_email(to_address: str, subject: str, text_body: str, html_body: str | None = None) -> bool:
    cfg = current_app.config
    host = (cfg.get("SMTP_HOST") or "").strip()
    username = (cfg.get("SMTP_USERNAME") or "").strip()
    password = (cfg.get("SMTP_PASSWORD") or "").strip().replace(" ", "")
    sender = (cfg.get("MAIL_FROM") or username).strip()
    if current_app.testing:
        current_app.extensions.setdefault("mail_test_outbox", []).append({
            "to": to_address, "subject": subject, "text": text_body,
        })
        return True
    if not host or not username or not password or not sender:
        if cfg.get("APP_ENV", "development") != "production" and cfg.get("OTP_DEV_MODE", True):
            current_app.logger.warning("MAIL DEV MODE: %s | %s", to_address, text_body)
            current_app.extensions.setdefault("mail_dev_outbox", []).append({
                "to": to_address, "subject": subject, "text": text_body,
            })
            return True
        raise RuntimeError("Email delivery is not configured. Add SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD and MAIL_FROM.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_address
    message.set_content(text_body)
    if html_body:
        message.add_alternative(html_body, subtype="html")
    port = int(cfg.get("SMTP_PORT", 587))
    context = ssl.create_default_context()
    timeout = int(cfg.get("SMTP_TIMEOUT_SECONDS", 20))
    if cfg.get("SMTP_USE_SSL", False):
        with smtplib.SMTP_SSL(host, port, timeout=timeout, context=context) as server:
            server.login(username, password)
            server.send_message(message)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as server:
            server.ehlo()
            if cfg.get("SMTP_USE_TLS", True):
                server.starttls(context=context)
                server.ehlo()
            server.login(username, password)
            server.send_message(message)
    return True
