import unittest
import wsgiref.headers
import wsgiref.util

from .server import application


class StartResponseMock:
    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        return self.write

    def write(self, body_data):  # pragma: no cover
        raise NotImplementedError


def request(method, url):
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": url,
    }
    wsgiref.util.setup_testing_defaults(environ)
    start_response = StartResponseMock()

    iterable = application(environ, start_response)

    status_code = int(start_response.status.split()[0])
    response_headers = wsgiref.headers.Headers(start_response.headers)
    body = b"".join(iterable).decode()
    assert start_response.exc_info is None
    return status_code, response_headers, body


class TestServer(unittest.TestCase):
    def test_new_grid(self):
        status, headers, body = request("GET", "/")

        self.assertEqual(status, 302)
        self.assertTrue(headers["Location"].startswith("/problem/"))

    def test_problem(self):
        url = "/problem/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79"
        status, headers, body = request("GET", url)

        self.assertEqual(status, 200)
        self.assertIn("★☆☆☆☆", body)
        self.assertIn(
            "<table><tr><td>5</td><td>3</td><td contenteditable></td><td contenteditable></td><td>7</td>",
            body,
        )

    def test_problem_bad_request(self):
        for url, error in [
            (
                "/problem/53__7____6__A95____98____6_8___6___34__8_3__A7___2___6_6____28____4A9__5____8__79",
                "cell contains invalid value: 'A'",
            ),
            (
                "/problem/531_7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
                "no solution found",
            ),
            (
                "/problem/____7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
                "multiple solutions found",
            ),
        ]:
            with self.subTest(url=url):
                status, headers, body = request("GET", url)

                self.assertEqual(status, 400)
                self.assertIn(error, body)

    def test_solution(self):
        url = "/solution/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79"
        status, headers, body = request("GET", url)

        self.assertEqual(status, 200)
        self.assertIn("★☆☆☆☆", body)
        self.assertIn(
            "<table><tr><td>5</td><td>3</td><td>4</td><td>6</td><td>7</td>", body
        )

    def test_solution_bad_request(self):
        for url, error in [
            (
                "/solution/53__7____6__A95____98____6_8___6___34__8_3__A7___2___6_6____28____4A9__5____8__79",
                "cell contains invalid value: 'A'",
            ),
            (
                "/solution/531_7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
                "no solution found",
            ),
            (
                "/solution/____7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
                "multiple solutions found",
            ),
        ]:
            with self.subTest(url=url):
                status, headers, body = request("GET", url)

                self.assertEqual(status, 400)
                self.assertIn(error, body)

    def test_post_method(self):
        for url in [
            "/",
            "/problem/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
            "/solution/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
        ]:
            with self.subTest(url=url):
                status, headers, body = request("POST", url)

                self.assertEqual(status, 405)

    def test_unknown_url(self):
        status, headers, body = request("GET", "/admin/")

        self.assertEqual(status, 404)
