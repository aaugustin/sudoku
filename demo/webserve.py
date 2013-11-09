#!/usr/bin/env python
# Copyright (c) 2008-2009 Aymeric Augustin

"""Web server to demonstrate the SuDoKu generator."""

import BaseHTTPServer
import datetime
import os.path
import sys
import time
import webbrowser
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path[:0] = [BASEDIR]
from sudoku import SuDoKu


SERVER_ADDRESS = ('localhost', 55729)   # port number actually means something
                                        # but I don't remember what! my guess:
                                        # 22 4 85 -> 55 7 118 -> 55 7 29

TEMPLATE = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
                      "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
  <meta http-equiv="Content-Type"
        content="application/xhtml+xml; charset=utf-8" />
  <title>SuDoKu solver and generator</title>
  <style type="text/css">
.grid       { width: 50%%; float: left; }
.sudoku     { margin: 1em auto; border: 2px solid black;
              border-collapse: collapse; }
.sudoku td  { width: 1.5em; height: 1.5em;
              border: 1px solid black; font-size: 1.25em;
              text-align: center; vertical-align: middle; }
.time       { text-align: center; }
.difficulty { margin: 2em; clear: left;
              text-align: center; font-weight: bold; }
.copyright  { border-top: 1px solid gray; padding: 0.5em;
              font-size: 0.825em; }
  </style>
  </head>
<body>
<div class="grid">
  %(gen)s
  <div class="time">Generation: %(gen_t).2fms</div>
</div>
<div class="grid">
  %(res)s
  <div class="time">Resolution: %(res_t).2fms</div>
</div>
<div class="difficulty">Difficulty: %(dif).2f - <a href="/">New grid</a></div>
<div class="copyright">Copyright (c) 2008-%(year)d Aymeric Augustin</div>
</body>
</html>
"""


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != '/':
            self.send_error(404)
            return
        s = SuDoKu()
        t0 = time.time()
        generated = s.generate()
        t1 = time.time()
        resolved = s.resolve()[0]
        t2 = time.time()
        difficulty = s.estimate()[0]
        substitutions = {
            'gen': s.to_string('html', generated),
            'gen_t': (t1 - t0) * 1000,
            'res': s.to_string('html', resolved),
            'res_t': (t2 - t1) * 1000,
            'dif': difficulty,
            'year': datetime.date.today().year,
        }
        html = TEMPLATE % substitutions
        self.send_response(200)
        self.send_header('Content-Type', 'application/xhtml+xml')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, *args):
        pass

class Server(BaseHTTPServer.HTTPServer):

    def run(self):
        sys.stdout.write("Server is running at http://%s:%d/\n" %
                         (self.server_name, self.server_port))
        sys.stdout.write("Quit the server with ^C.\n")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            sys.stdout.write('\n')


if __name__ == '__main__':
    server = Server(SERVER_ADDRESS, Handler)
    webbrowser.open('http://%s:%d/' % SERVER_ADDRESS)
    server.run()
