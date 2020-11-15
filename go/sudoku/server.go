package sudoku

import (
	"html/template"
	"math"
	"net/http"
	"strings"
)

// http.Handler for the web server.
var Handler http.Handler

func init() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", handleRoot)
	mux.HandleFunc("/problem/", handleProblem)
	mux.HandleFunc("/solution/", handleSolution)
	Handler = requireGet(mux)
}

type Context struct {
	Stars   string
	Display template.HTML
	Link    template.HTML
}

var t = template.Must(template.New("").Parse(`<!DOCTYPE html>
<html lang="en">
    <head>
        <meta name="viewport" content="initial-scale=1">
        <title>Sudoku</title>
        <style>
html {
    height: 100%;
}
body {
    margin: 0;
    min-height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-evenly;
}
table {
    border: 2px solid #000;
    border-collapse: collapse;
}
td  {
    width: 2em;
    height: 2em;
    border: 1px solid #bbb;
    text-align: center;
    vertical-align: middle;
    line-height: 1;
}
tr:nth-child(3n) td {
    border-bottom-color: #000;
}
td:nth-child(3n) {
    border-right-color: #000;
}
td[contenteditable] {
    font-weight: bold;
    color: #666;
}
header, footer {
    font-family: "Helvetica Neue", sans-serif;
    font-weight: 300;
    color: #888;
    padding: 1em;
}
a {
    color: #888;
}
a:hover {
    color: #444;
}
@media screen and (min-width: 480px) {
    table {
        font-size: 1.5em;
    }
}
@media screen and (min-width: 720px) {
    table  {
        font-size: 2em;
    }
}
@media print {
    table    {
        font-size: 1.5em;
    }
    header, footer {
        display: none;
    }
}
        </style>
    </head>
    <body>
        <header>
            {{.Stars}}
        </header>
        {{.Display}}
        <footer>
            <a href="/">New grid</a>
            -
            <a href="/problem/{{.Link}}">Problem</a>
            -
            <a href="/solution/{{.Link}}">Solution</a>
        </footer>
    </body>
</html>
`))

func renderGrid(w http.ResponseWriter, display *Grid, link *Grid, difficulty float64) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	stars := int(math.Min(difficulty, 5.0))
	c := Context{
		Stars: strings.Repeat("★", stars) + strings.Repeat("☆", 5-stars),
		Display: template.HTML(strings.ReplaceAll(
			display.toHTML(),
			"<td></td>",
			"<td contenteditable></td>",
		)),
		Link: template.HTML(link.toLine()),
	}
	err := t.Execute(w, c)
	if err != nil {
		panic("error rendering template")
	}
}

func handleRoot(w http.ResponseWriter, r *http.Request) {
	if r.URL.Path != "/" {
		http.Error(w, r.URL.Path+" not found", 404)
		return
	}
	handleNewGrid(w, r)
}

func handleNewGrid(w http.ResponseWriter, r *http.Request) {
	grid, _ := Generate()
	http.Redirect(w, r, "/problem/"+grid.toLine(), 302)
}

func handleProblem(w http.ResponseWriter, r *http.Request) {
	problem := r.URL.Path[len("/problem/"):]
	grid, err := NewGridFromString(problem)
	if err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	solutions, difficulty := Solve(&grid)
	if len(solutions) == 0 {
		http.Error(w, "no solution found", 400)
		return
	}
	if len(solutions) > 1 {
		http.Error(w, "multiple solutions found", 400)
		return
	}
	renderGrid(w, &grid, &grid, difficulty)
}

func handleSolution(w http.ResponseWriter, r *http.Request) {
	problem := r.URL.Path[len("/solution/"):]
	grid, err := NewGridFromString(problem)
	if err != nil {
		http.Error(w, err.Error(), 400)
		return
	}
	solutions, difficulty := Solve(&grid)
	if len(solutions) == 0 {
		http.Error(w, "no solution found", 400)
		return
	}
	if len(solutions) > 1 {
		http.Error(w, "multiple solutions found", 400)
		return
	}
	renderGrid(w, &solutions[0], &grid, difficulty)
}

// requireGet returns a HTTP 405 error for methods other than GET.
func requireGet(h http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "GET" {
			http.Error(w, r.Method+" not allowed", 405)
			return
		}
		h.ServeHTTP(w, r)
	})
}
