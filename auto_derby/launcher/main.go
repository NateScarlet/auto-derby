package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"runtime"

	"github.com/jchv/go-webview-selector"
)

func bootstrapWebview2() (ok bool, err error) {
	if runtime.GOOS != "windows" {
		return
	}
	// download
	filename, err := func() (filename string, err error) {
		resp, err := http.Get("https://go.microsoft.com/fwlink/p/?LinkId=2124703")
		if err != nil {
			return
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			err = fmt.Errorf("bootstrapWebview: request failed: %d", resp.StatusCode)
			return
		}
		f, err := os.CreateTemp(os.TempDir(), "webview2-bootstrap-*.exe")
		if err != nil {
			return
		}
		defer f.Close()
		_, err = io.Copy(f, resp.Body)
		if err != nil {
			return
		}
		return f.Name(), nil
	}()
	if err != nil {
		return
	}
	defer os.Remove(filename)
	err = exec.Command(filename).Run()
	if err != nil {
		return
	}
	return true, nil
}

func main() {
	w := webview.New(false)
	if w == nil {
		ok, err := bootstrapWebview2()
		if err != nil {
			log.Fatalf("bootstrap failed: %s\n", err)
			return
		}
		if !ok {
			log.Fatalln("failed to load webview")
		}
		main()
		return
	}
	defer w.Destroy()
	w.SetSize(800, 600, webview.HintFixed)
	w.Navigate("https://example.com")
	w.Run()
}
