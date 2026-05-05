from __future__ import annotations


class CDSDownloadError(Exception):
    pass


class CacheReadError(Exception):
    pass


class InvalidSelectionError(Exception):
    pass