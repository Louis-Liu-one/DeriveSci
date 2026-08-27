package main

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"

)

const sessionCookie = "derivesci_session"

func (app *application) registerAuthRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /api/user/login", app.apiUserLogin)
	mux.HandleFunc("POST /api/user/register", app.apiUserRegister)
	mux.HandleFunc("POST /api/user/edit-profile", app.apiEditProfile)
	mux.HandleFunc("POST /api/user/edit-introduction", app.apiEditIntroduction)
	mux.HandleFunc("POST /api/user/logout", app.apiUserLogout)
	mux.HandleFunc("POST /api/user/unregister", app.apiUserUnregister)
	mux.HandleFunc("GET /auth/avatars/{uid}", app.avatarFile)
}

func (app *application) apiUserLogin(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid login form")
		return
	}
	name, err := trimRequired(r.FormValue("username"), "username", 64)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	password := r.FormValue("password")
	if password == "" {
		writeAPIError(w, http.StatusBadRequest, "password is required")
		return
	}

	user, err := app.findUserByName(r.Context(), name)
	if err != nil || !verifyPassword(user.PasswordHash, password) {
		writeAPIError(w, http.StatusBadRequest, "invalid username or password")
		return
	}
	if !strings.HasPrefix(user.PasswordHash, "$2") {
		if upgraded, hashErr := hashPassword(password); hashErr == nil {
			_, _ = app.db.ExecContext(r.Context(), "UPDATE users SET password = ? WHERE uid = ?", upgraded, user.ID)
		}
	}
	if err := app.setSession(w, user.ID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create session")
		return
	}
	writeJSON(w, http.StatusOK, map[string]bool{"ok": true})
}

func (app *application) apiUserRegister(w http.ResponseWriter, r *http.Request) {
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid registration form")
		return
	}
	name, err := trimRequired(r.FormValue("username"), "username", 64)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	password := r.FormValue("password")
	if len(password) < 8 || len(password) > 256 {
		writeAPIError(w, http.StatusBadRequest, "password must contain 8 to 256 characters")
		return
	}
	if password != r.FormValue("password_confirmation") {
		writeAPIError(w, http.StatusBadRequest, "password confirmation does not match")
		return
	}
	gender, err := formInteger(r, "gender", 0, 0, 2)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	passwordHash, err := hashPassword(password)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not secure password")
		return
	}
	avatar, mimeType, err := formImage(r, "avatar")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}

	now := time.Now().UTC()
	result, err := app.db.ExecContext(r.Context(), `
		INSERT INTO users (name, gender, password, avatar, avmimetype, avlastmodified, cmtlastvisit)
		VALUES (?, ?, ?, ?, ?, ?, ?)`, name, gender, passwordHash, avatar, mimeType, now, now)
	if err != nil {
		if isUniqueViolation(err) {
			writeAPIError(w, http.StatusConflict, "username already exists")
			return
		}
		writeAPIError(w, http.StatusInternalServerError, "could not create user")
		return
	}
	userID, _ := result.LastInsertId()
	if err := app.setSession(w, userID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create session")
		return
	}
	writeJSON(w, http.StatusCreated, map[string]bool{"ok": true})
}

func (app *application) apiEditProfile(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid profile form")
		return
	}
	name, err := trimRequired(r.FormValue("username"), "username", 64)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	gender, err := formInteger(r, "gender", current.Gender, 0, 2)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	password := r.FormValue("password")
	if password != r.FormValue("password_confirmation") {
		writeAPIError(w, http.StatusBadRequest, "password confirmation does not match")
		return
	}
	if password != "" && (len(password) < 8 || len(password) > 256) {
		writeAPIError(w, http.StatusBadRequest, "password must contain 8 to 256 characters")
		return
	}
	avatar, mimeType, err := formImage(r, "avatar")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}

	query := "UPDATE users SET name = ?, gender = ?"
	args := []any{name, gender}
	if password != "" {
		hash, err := hashPassword(password)
		if err != nil {
			writeAPIError(w, http.StatusInternalServerError, "could not secure password")
			return
		}
		query += ", password = ?"
		args = append(args, hash)
	}
	if avatar != nil {
		query += ", avatar = ?, avmimetype = ?, avlastmodified = ?"
		args = append(args, avatar, mimeType, time.Now().UTC())
	}
	query += " WHERE uid = ?"
	args = append(args, current.ID)
	if _, err := app.db.ExecContext(r.Context(), query, args...); err != nil {
		if isUniqueViolation(err) {
			writeAPIError(w, http.StatusConflict, "username already exists")
			return
		}
		writeAPIError(w, http.StatusInternalServerError, "could not update profile")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/auth/welcome"})
}

func (app *application) apiEditIntroduction(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	var body struct {
		Introduction string `json:"introduction"`
	}
	if err := decodeJSONBody(r, &body); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	if len([]rune(body.Introduction)) > 8_000 {
		writeAPIError(w, http.StatusBadRequest, "introduction must be at most 8000 characters")
		return
	}
	if _, err := app.db.ExecContext(r.Context(), "UPDATE users SET introduction = ? WHERE uid = ?", body.Introduction, current.ID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update introduction")
		return
	}
	writeJSON(w, http.StatusOK, map[string]bool{"ok": true})
}

func (app *application) apiUserLogout(w http.ResponseWriter, r *http.Request) {
	if _, ok := app.requireUser(w, r); !ok {
		return
	}
	app.clearSession(w)
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/"})
}

func (app *application) apiUserUnregister(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if _, err := app.db.ExecContext(r.Context(), "DELETE FROM users WHERE uid = ?", current.ID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete user")
		return
	}
	app.clearSession(w)
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/"})
}

func (app *application) avatarFile(w http.ResponseWriter, r *http.Request) {
	id, err := pathID(r, "uid")
	if err != nil {
		http.NotFound(w, r)
		return
	}
	var data []byte
	var mimeType string
	var modified time.Time
	err = app.db.QueryRowContext(r.Context(), "SELECT avatar, avmimetype, avlastmodified FROM users WHERE uid = ?", id).Scan(&data, &mimeType, &modified)
	if errors.Is(err, sql.ErrNoRows) || len(data) == 0 {
		http.NotFound(w, r)
		return
	}
	if err != nil {
		http.Error(w, "could not read avatar", http.StatusInternalServerError)
		return
	}
	if mimeType == "" {
		mimeType = http.DetectContentType(data)
	}
	w.Header().Set("Content-Type", mimeType)
	w.Header().Set("Cache-Control", "public, max-age=600")
	http.ServeContent(w, r, "avatar", modified, bytes.NewReader(data))
}

func (app *application) setSession(w http.ResponseWriter, userID int64) error {
	encoded, err := app.cookies.Encode(sessionCookie, map[string]int64{"uid": userID})
	if err != nil {
		return err
	}
	http.SetCookie(w, &http.Cookie{
		Name:     sessionCookie,
		Value:    encoded,
		Path:     "/",
		MaxAge:   60 * 60 * 24 * 14,
		HttpOnly: true,
		Secure:   app.config.cookieSecure,
		SameSite: http.SameSiteLaxMode,
	})
	return nil
}

func (app *application) clearSession(w http.ResponseWriter) {
	http.SetCookie(w, &http.Cookie{Name: sessionCookie, Value: "", Path: "/", MaxAge: -1, HttpOnly: true, Secure: app.config.cookieSecure, SameSite: http.SameSiteLaxMode})
}

func (app *application) currentUser(r *http.Request) (*user, error) {
	cookie, err := r.Cookie(sessionCookie)
	if err != nil {
		return nil, err
	}
	values := map[string]int64{}
	if err := app.cookies.Decode(sessionCookie, cookie.Value, &values); err != nil {
		return nil, err
	}
	return app.findUserByID(r.Context(), values["uid"])
}

func (app *application) requireUser(w http.ResponseWriter, r *http.Request) (*user, bool) {
	user, err := app.currentUser(r)
	if err != nil {
		writeAPIError(w, http.StatusUnauthorized, "login required")
		return nil, false
	}
	return user, true
}

func (app *application) requireAdmin(w http.ResponseWriter, r *http.Request) (*user, bool) {
	user, ok := app.requireUser(w, r)
	if !ok {
		return nil, false
	}
	if !user.IsAdmin {
		writeAPIError(w, http.StatusForbidden, "administrator access required")
		return nil, false
	}
	return user, true
}

func (app *application) findUserByID(ctx context.Context, id int64) (*user, error) {
	return app.scanUser(app.db.QueryRowContext(ctx, `SELECT uid, name, gender, password, COALESCE(introduction, ''), avatar, COALESCE(avmimetype, ''), COALESCE(avlastmodified, CURRENT_TIMESTAMP), COALESCE(cmtlastvisit, CURRENT_TIMESTAMP), isadmin FROM users WHERE uid = ?`, id))
}

func (app *application) findUserByName(ctx context.Context, name string) (*user, error) {
	return app.scanUser(app.db.QueryRowContext(ctx, `SELECT uid, name, gender, password, COALESCE(introduction, ''), avatar, COALESCE(avmimetype, ''), COALESCE(avlastmodified, CURRENT_TIMESTAMP), COALESCE(cmtlastvisit, CURRENT_TIMESTAMP), isadmin FROM users WHERE name = ?`, name))
}

type rowScanner interface{ Scan(...any) error }

func (app *application) scanUser(row rowScanner) (*user, error) {
	var value user
	if err := row.Scan(&value.ID, &value.Name, &value.Gender, &value.PasswordHash, &value.Introduction, &value.Avatar, &value.AvatarType, &value.AvatarTime, &value.CommentVisit, &value.IsAdmin); err != nil {
		return nil, err
	}
	return &value, nil
}

func formInteger(r *http.Request, field string, fallback, min, max int) (int, error) {
	value := r.FormValue(field)
	if value == "" {
		return fallback, nil
	}
	var number int
	if _, err := fmt.Sscan(value, &number); err != nil || number < min || number > max {
		return 0, fmt.Errorf("%s is invalid", field)
	}
	return number, nil
}

func formImage(r *http.Request, field string) ([]byte, string, error) {
	file, header, err := r.FormFile(field)
	if errors.Is(err, http.ErrMissingFile) {
		return nil, "", nil
	}
	if err != nil {
		return nil, "", fmt.Errorf("invalid %s upload", field)
	}
	defer file.Close()
	data, mimeType, err := readValidatedImage(file)
	if err != nil {
		return nil, "", fmt.Errorf("%s: %w", field, err)
	}
	_ = header
	return data, mimeType, nil
}

func decodeJSONBody(r *http.Request, target any) error {
	r.Body = http.MaxBytesReader(nil, r.Body, maxRequestBody)
	decoder := json.NewDecoder(r.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return err
	}
	if decoder.More() {
		return errors.New("unexpected JSON values")
	}
	return nil
}

func isUniqueViolation(err error) bool {
	return strings.Contains(strings.ToLower(err.Error()), "unique")
}
