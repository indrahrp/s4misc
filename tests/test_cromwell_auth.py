"""
Tests for cromwell basic authentication over https.

Because we generate a self-signed certificate, we must ignore the
SSL verification features of requests in order to complete the requests.

Make sure you have pytest, requests, and cromwell_tools installed before
running.

Usage:
    1. Edit the url in the cromwell_url() fixture
    2. Edit the username and password in the cromwell_auth() fixture
"""

import pytest
from cromwell_tools.cromwell_auth import CromwellAuth
from cromwell_tools import api
import requests
import contextlib
import warnings

from urllib3.exceptions import InsecureRequestWarning

old_merge_environment_settings = requests.Session.merge_environment_settings


@pytest.fixture(scope="module")
def cromwell_url():
    return "https://ec2-54-164-58-179.compute-1.amazonaws.com"


@pytest.fixture(scope="module")
def cromwell_auth(cromwell_url):
    url = cromwell_url
    username = "cromwell"
    password = "Usewdl2019!"

    auth = CromwellAuth.harmonize_credentials(
        url=url, username=username, password=password
    )
    return auth


@contextlib.contextmanager
def no_ssl_verification():
    opened_adapters = set()

    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        # Verification happens only once per connection so we need to close
        # all the opened adapters once we're done. Otherwise, the effects of
        # verify=False persist beyond the end of this context manager.
        opened_adapters.add(self.get_adapter(url))

        settings = old_merge_environment_settings(
            self, url, proxies, stream, verify, cert
        )
        settings["verify"] = False

        return settings

    requests.Session.merge_environment_settings = merge_environment_settings

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", InsecureRequestWarning)
            yield
    finally:
        requests.Session.merge_environment_settings = old_merge_environment_settings

        for adapter in opened_adapters:
            try:
                adapter.close()
            except Exception:
                pass


def test_cromwell_auth(cromwell_auth: CromwellAuth):
    assert "https" in cromwell_auth.url
    with no_ssl_verification():
        health = api.health(cromwell_auth)
        assert health.ok is True
        assert "Engine Database" in health.json()
