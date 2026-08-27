package main

import (
	"database/sql"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"
)

const (
	maxRequestBody = 5 << 20
	maxImageSize   = 2 << 20
)

var (
	errNotFound  = errors.New("not found")
	errForbidden = errors.New("forbidden")
)

type user struct {
	ID           int64
	Name         string
	Gender       int
	PasswordHash string
	Introduction string
	Avatar       []byte
	AvatarType   string
	AvatarTime   time.Time
	CommentVisit time.Time
	IsAdmin      bool
}

type problem struct {
	Number        string
	Title         string
	Statement     string
	Answer        string
	SourceID      sql.NullInt64
	ReviewStatus  int
	IsOfficial    bool
	ReviewComment string
}

type solution struct {
	ProblemNumber string
	Number        int
	UserID        sql.NullInt64
	Title         string
	Content       string
}

type article struct {
	ID      int64
	UserID  sql.NullInt64
	Title   string
	Content string
}

type uploadedImage struct {
	PostType  int
	PostIdent string
	Name      string
	UserID    sql.NullInt64
	Size      int64
	MIMEType  string
	Data      []byte
}

type comment struct {
	ID        int64
	UserID    sql.NullInt64
	Content   string
	Timestamp time.Time
	ReplyToID sql.NullInt64
	PostType  int
	PostIdent string
}

func trimRequired(value, field string, maximum int) (string, error) {
	value = strings.TrimSpace(value)
	if value == "" {
		return "", fmt.Errorf("%s is required", field)
	}
	if len([]rune(value)) > maximum {
		return "", fmt.Errorf("%s must be at most %d characters", field, maximum)
	}
	return value, nil
}

func trimOptional(value string, maximum int) (string, error) {
	value = strings.TrimSpace(value)
	if len([]rune(value)) > maximum {
		return "", fmt.Errorf("value must be at most %d characters", maximum)
	}
	return value, nil
}

func apiError(message string) map[string]any {
	return map[string]any{"ok": false, "error": message}
}

func writeAPIError(w http.ResponseWriter, status int, message string) {
	writeJSON(w, status, apiError(message))
}

func asHTTPError(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, errNotFound):
		writeAPIError(w, http.StatusNotFound, "resource not found")
	case errors.Is(err, errForbidden):
		writeAPIError(w, http.StatusForbidden, "forbidden")
	default:
		writeAPIError(w, http.StatusBadRequest, err.Error())
	}
}

func parseBool(value string) bool {
	return value == "1" || strings.EqualFold(value, "true") || strings.EqualFold(value, "on")
}
