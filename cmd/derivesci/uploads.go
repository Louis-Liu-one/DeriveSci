package main

import (
	"bytes"
	"fmt"
	"image"
	_ "image/gif"
	_ "image/jpeg"
	_ "image/png"
	"io"
	"net/http"
	"strings"
)

func readValidatedImage(file io.Reader) ([]byte, string, error) {
	data, err := io.ReadAll(io.LimitReader(file, maxImageSize+1))
	if err != nil || len(data) > maxImageSize || len(data) == 0 {
		return nil, "", fmt.Errorf("image must be no larger than 2 MiB")
	}
	mimeType := http.DetectContentType(data)
	if mimeType != "image/jpeg" && mimeType != "image/png" && mimeType != "image/gif" && mimeType != "image/webp" {
		return nil, "", fmt.Errorf("image must be a PNG, JPEG, GIF, or WebP image")
	}
	if mimeType != "image/webp" {
		if _, _, err := image.DecodeConfig(bytes.NewReader(data)); err != nil {
			return nil, "", fmt.Errorf("image is invalid")
		}
	}
	return data, mimeType, nil
}

func safeContentType(contentType string) string {
	if strings.HasPrefix(contentType, "image/") {
		return contentType
	}
	return "application/octet-stream"
}
