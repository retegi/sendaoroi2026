import gettext
from pathlib import Path

from asgiref.local import Local

from django.conf import settings
from django.utils.translation import trans_real


class TranslationReloadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._catalog_signature = None

    def __call__(self, request):
        catalog_signature = self._get_catalog_signature()
        if catalog_signature != self._catalog_signature:
            self._reset_translation_caches()
            self._catalog_signature = catalog_signature

        return self.get_response(request)

    @staticmethod
    def _reset_translation_caches():
        # Keep this in sync with Django's translation_file_changed handler.
        gettext._translations = {}
        trans_real._translations = {}
        trans_real._default = None
        trans_real._active = Local()

    @staticmethod
    def _get_catalog_signature():
        signature = []
        for locale_path in settings.LOCALE_PATHS:
            for catalog_path in Path(locale_path).rglob("*.mo"):
                try:
                    stat = catalog_path.stat()
                except OSError:
                    continue
                signature.append((str(catalog_path), stat.st_mtime_ns, stat.st_size))
        return tuple(sorted(signature))