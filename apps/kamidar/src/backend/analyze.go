package main

import (
    "os/exec"
    "log"
)

func runAnalysis(file string, color string) string {
    log.Println("python3","analyze.py","--image_source=" + file, "--color_input=" + color)
    out, _ := exec.Command("python3","analyze.py","--image_source=" + file, "--color_input=" + color,"--gps=1,2").CombinedOutput()
    log.Println(string(out))
	return string(out)
}