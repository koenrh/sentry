"""
sentry.utils.http
~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2012 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import urllib
from urlparse import urlparse

from sentry.conf import settings
from sentry.plugins.helpers import get_option


def safe_urlencode(params, doseq=0):
    """
    UTF-8-safe version of safe_urlencode

    The stdlib safe_urlencode prior to Python 3.x chokes on UTF-8 values
    which can't fail down to ascii.
    """
    # Snippet originally from pysolr: https://github.com/toastdriven/pysolr

    if hasattr(params, "items"):
        params = params.items()

    new_params = list()

    for k, v in params:
        k = k.encode("utf-8")

        if isinstance(v, basestring):
            new_params.append((k, v.encode("utf-8")))
        elif isinstance(v, (list, tuple)):
            new_params.append((k, [i.encode("utf-8") for i in v]))
        else:
            new_params.append((k, unicode(v)))

    return urllib.urlencode(new_params, doseq)


def is_same_domain(url1, url2):
    """
    Returns true if the two urls should be treated as if they're from the same
    domain (trusted).
    """
    url1 = urlparse(url1)
    url2 = urlparse(url2)
    return url1.netloc == url2.netloc


def get_origins(project=None):
    if settings.ALLOW_ORIGIN == '*':
        return '*'
    elif settings.ALLOW_ORIGIN:
        result = settings.ALLOW_ORIGIN.split(' ')
    else:
        result = []

    if project:
        optval = get_option('sentry:origins', project)
        if optval:
            result.extend(map(lambda x: x.lower(), optval))

    return frozenset(filter(bool, result))


def is_valid_origin(origin, project=None):
    allowed = get_origins(project)
    if allowed == '*':
        return True

    if not origin:
        return False

    return origin in allowed


def apply_access_control_headers(response, origin):
    """
    Provides the Access-Control headers to enable cross-site HTTP requests. You
    can find more information about these headers here:
    https://developer.mozilla.org/En/HTTP_access_control#Simple_requests
    """
    if origin:
        response['Access-Control-Allow-Origin'] = origin

    return response
