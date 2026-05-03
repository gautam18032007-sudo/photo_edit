import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

def _send(to: str, subject: str, html: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to
    msg.attach(MIMEText(html, "html"))
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.starttls()
            s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.sendmail(settings.FROM_EMAIL, to, msg.as_string())
    except Exception as e:
        logger.error(f"Email send failed to {to}: {e}")

def send_otp_email(to: str, otp: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:2rem;">
      <h2 style="color:#0F6E56;">PixelMind — Verify your email</h2>
      <p>Your one-time code:</p>
      <div style="font-size:2rem;font-weight:bold;letter-spacing:.4em;padding:1rem;background:#f0f7f4;border-radius:8px;text-align:center;">{otp}</div>
      <p style="color:#888;font-size:.85rem;">Expires in {settings.OTP_EXPIRE_MINUTES} minutes. Do not share this code.</p>
    </div>"""
    _send(to, "Your PixelMind verification code", html)

def send_welcome_email(to: str, name: str):
    html = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:auto;padding:2rem;">
      <h2 style="color:#0F6E56;">Welcome to PixelMind, {name}! 🎉</h2>
      <p>Your account is ready. Start editing photos, videos, and audio with AI.</p>
      <a href="https://app.pixelmind.app/dashboard"
         style="display:inline-block;background:#1D9E75;color:#fff;padding:.75rem 1.5rem;border-radius:2rem;text-decoration:none;margin-top:1rem;">
        Open Dashboard →
      </a>
    </div>"""
    _send(to, "Welcome to PixelMind", html)
