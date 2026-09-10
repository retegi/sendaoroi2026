import json
import logging
import time
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


logger = logging.getLogger(__name__)


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR") or "unknown"


def check_rate_limit(request):
    key = f"contact-form-rate:{get_client_ip(request)}"
    if cache.add(key, 1, settings.CONTACT_FORM_RATE_LIMIT_WINDOW):
        return settings.CONTACT_FORM_RATE_LIMIT_MAX >= 1
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, settings.CONTACT_FORM_RATE_LIMIT_WINDOW)
        return True
    return count <= settings.CONTACT_FORM_RATE_LIMIT_MAX


def verify_turnstile(request, token):
    if not settings.TURNSTILE_SITE_KEY and not settings.TURNSTILE_SECRET_KEY:
        return settings.DEBUG
    if not settings.TURNSTILE_SECRET_KEY or not token:
        return False

    payload = urlencode(
        {
            "secret": settings.TURNSTILE_SECRET_KEY,
            "response": token,
            "remoteip": get_client_ip(request),
        }
    ).encode()
    cloudflare_request = Request(
        settings.TURNSTILE_VERIFY_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urlopen(cloudflare_request, timeout=settings.TURNSTILE_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        logger.exception("contact_form_turnstile_error")
        return False

    return result.get("success") is True


def signed_form_timestamp():
    from django.core.signing import dumps

    return dumps(time.time(), salt=settings.CONTACT_FORM_TIMESTAMP_SALT)