package main

import (
    "os"
    "log"
    "time"
    "github.com/gin-gonic/gin"
    "net/http"
    "strconv"
    "encoding/json"

)

// UploadHandler handles POST /upload and saves the uploaded file to a directory
func UploadHandler(c *gin.Context) {
    file, _ := c.FormFile("file")
    log.Println(file.Filename)

    // Get extra parameters
    gps := c.PostForm("gps")
    color := c.PostForm("color")

    // Upload the file to specific dst.
    // Get upload directory from environment variable or use default
    DEST_UPLOAD := os.Getenv("DEST_UPLOAD")
    if DEST_UPLOAD == "" {
        DEST_UPLOAD = "./files/"
    }

    // Generate last 4 digits of timestamp as string
    ts := strconv.FormatInt(time.Now().Unix(), 10)
    last4 := ts
    if len(ts) > 4 {
        last4 = ts[len(ts)-4:]
    }
    filename := "photo-" + last4 + ".png"

    c.SaveUploadedFile(file, DEST_UPLOAD+filename)
    log.Println(gps,color)

    result := runAnalysis(DEST_UPLOAD+filename, color)
    log.Println(result)
    var resultData map[string]interface{}
    if err := json.Unmarshal([]byte(result), &resultData); err != nil {
        resultData = map[string]interface{}{
            "output": result,
            "error": "Failed to parse analysis output as JSON",
        }
    }

    c.JSON(http.StatusOK, gin.H{
        "data": resultData,
        "gps": gps,
        "color": color,
        "filename": filename,
    })   
}