"""Serves a directory on localhost without letting browsers cache it.
Usage: serve-web.py DIRECTORY PORT"""

import functools
import http.server
import sys


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        # Never answer 304 Not Modified, whatever the browser has cached.
        del self.headers["If-Modified-Since"]
        return super().send_head()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


directory, port = sys.argv[1], int(sys.argv[2])
handler = functools.partial(NoCacheHandler, directory=directory)
http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
