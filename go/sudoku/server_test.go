package sudoku

import (
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

type response struct {
	Code   int
	Header http.Header
	Body   string
}

func request(method string, url string) response {
	req := httptest.NewRequest(method, url, nil)
	w := httptest.NewRecorder()

	Handler.ServeHTTP(w, req)
	resp := w.Result()
	body, _ := ioutil.ReadAll(resp.Body)

	return response{resp.StatusCode, resp.Header, string(body)}
}

func TestNewGrid(t *testing.T) {
	url := "/"
	resp := request("GET", url)

	if resp.Code != 302 {
		t.Errorf("GET %s: got response code %d, want 302", url, resp.Code)
	}
	location := resp.Header.Get("Location")
	if !strings.HasPrefix(location, "/problem/") {
		t.Errorf("GET %s: got redirection to %s, want /problem/...", url, location)
	}
}

func TestProblem(t *testing.T) {
	url := "/problem/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79"
	resp := request("GET", url)

	if resp.Code != 200 {
		t.Errorf("GET %s: got response code %d, want 200", url, resp.Code)
	}
	if !strings.Contains(resp.Body, "★☆☆☆☆") {
		t.Errorf("GET %s: difficulty not found in response", url)
	}
	if !strings.Contains(resp.Body, "<table><tr><td>5</td><td>3</td><td contenteditable></td><td contenteditable></td><td>7</td>") {
		t.Errorf("GET %s: problem not found in response", url)
	}
}

func TestProblemBadRequest(t *testing.T) {
	var tests = []struct {
		url   string
		error string
	}{
		{
			"/problem/53__7____6__A95____98____6_8___6___34__8_3__A7___2___6_6____28____4A9__5____8__79",
			"cell contains invalid value: 'A'",
		},
		{
			"/problem/531_7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
			"no solution found",
		},
		{
			"/problem/____7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
			"multiple solutions found",
		},
	}

	for _, test := range tests {
		resp := request("GET", test.url)

		if resp.Code != 400 {
			t.Errorf("GET %s: got response code %d, want 400", test.url, resp.Code)
		}
		if !strings.Contains(resp.Body, test.error) {
			t.Errorf("GET %s: error not found in response", test.url)
		}
	}
}

func TestSolution(t *testing.T) {
	url := "/solution/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79"
	resp := request("GET", url)

	if resp.Code != 200 {
		t.Errorf("GET %s: got response code %d, want 200", url, resp.Code)
	}
	if !strings.Contains(resp.Body, "★☆☆☆☆") {
		t.Errorf("GET %s: difficulty not found in response", url)
	}
	if !strings.Contains(resp.Body, "<table><tr><td>5</td><td>3</td><td>4</td><td>6</td><td>7</td>") {
		t.Errorf("GET %s: solution not found in response", url)
	}
}

func TestSolutionBadRequest(t *testing.T) {
	var tests = []struct {
		url   string
		error string
	}{
		{
			"/solution/53__7____6__A95____98____6_8___6___34__8_3__A7___2___6_6____28____4A9__5____8__79",
			"cell contains invalid value: 'A'",
		},
		{
			"/solution/531_7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
			"no solution found",
		},
		{
			"/solution/____7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
			"multiple solutions found",
		},
	}

	for _, test := range tests {
		resp := request("GET", test.url)

		if resp.Code != 400 {
			t.Errorf("GET %s: got response code %d, want 400", test.url, resp.Code)
		}
		if !strings.Contains(resp.Body, test.error) {
			t.Errorf("GET %s: error not found in response", test.url)
		}
	}
}

func TestPostMethod(t *testing.T) {
	var urls = []string{
		"/",
		"/problem/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
		"/solution/53__7____6__195____98____6_8___6___34__8_3__17___2___6_6____28____419__5____8__79",
	}
	for _, url := range urls {
		resp := request("POST", url)

		if resp.Code != 405 {
			t.Errorf("POST %s: got response code %d, want 405", url, resp.Code)
		}
	}
}

func TestUnknownURL(t *testing.T) {
	url := "/admin/"
	resp := request("GET", url)

	if resp.Code != 404 {
		t.Errorf("GET %s: got response code %d, want 404", url, resp.Code)
	}
}
