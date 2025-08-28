package main

import (
    "net/http"
	"fmt"
    "github.com/gin-gonic/gin"
	"github.com/gin-contrib/static"
)

func main() {
    router := gin.Default()
    router.MaxMultipartMemory = 8 << 20  // 8 MiB
    gin.SetMode(gin.DebugMode)
    router.Use(gin.Logger())

    router.GET("/hello", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "Hello, world!",
        })
    })

    router.POST("/upload", UploadHandler)
    //router.POST("/restart", RestartDeploymentHandler)
    //router.GET("/apps", GetNonSystemDeploymentsHandler)


    router.Use(static.Serve("/", static.LocalFile("../frontend/dist/spa", true)))//../frontend/dist/spa
    router.Use(static.Serve("/results", static.LocalFile("./results", true)))

	router.NoRoute(func(c *gin.Context) {
		fmt.Printf("%s doesn't exists, redirect on /\n", c.Request.URL.Path)
		c.Redirect(http.StatusMovedPermanently, "/")
	})

    // Listen and serve on 0.0.0.0:8080
    router.Run(":8080")
}