package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "hello from buildx demo on %s\n", r.UserAgent())
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("listening on :8080")
	http.ListenAndServe(":8080", nil)
}
