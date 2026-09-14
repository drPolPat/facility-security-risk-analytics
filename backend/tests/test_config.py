r"""CORS settings parsing.

A leading tab made it into CORS_ORIGIN_REGEX on Railway via a dashboard
paste (`\thttps://.*\.vercel\.app`) and silently broke every deployed
origin match -- no error, just a permanent "Disallowed CORS origin". These
tests pin the fix: whitespace is stripped before the value is used.
"""

from __future__ import annotations

import re

from app.config import Settings


def test_cors_origin_regex_strips_stray_whitespace():
    settings = Settings(cors_origin_regex="\thttps://.*\\.vercel\\.app\n")
    assert settings.cors_origin_regex == r"https://.*\.vercel\.app"


def test_stripped_regex_matches_a_real_vercel_origin():
    settings = Settings(cors_origin_regex="\thttps://.*\\.vercel\\.app")
    assert re.fullmatch(
        settings.cors_origin_regex, "https://facility-security-risk-analytics.vercel.app"
    )


def test_cors_origins_strips_stray_whitespace():
    settings = Settings(cors_origins="  http://localhost:5173  ")
    assert settings.cors_origins == "http://localhost:5173"
    assert settings.cors_origins_list == ["http://localhost:5173"]


def test_cors_origin_regex_none_is_left_alone():
    settings = Settings(cors_origin_regex=None)
    assert settings.cors_origin_regex is None
