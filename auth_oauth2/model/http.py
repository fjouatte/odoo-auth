import logging
import os
from openerp.addons.web import http
import time
_logger = logging.getLogger(__name__)


def custom_session_gc(session_store):
    deadline = time.time() - 60*120
    for fname in os.listdir(session_store.path):
        path = os.path.join(session_store.path, fname)
        try:
            if os.path.getmtime(path) < deadline:
                os.unlink(path)
            else:
                os.utime(path, None)
        except OSError:
            pass

http.session_gc = custom_session_gc
