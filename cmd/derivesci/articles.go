package main

import (
	"context"
	"database/sql"
	"errors"
	"net/http"
	"strconv"
	"time"
)

func (app *application) registerArticleRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /api/article/upload", app.apiUploadArticle)
	mux.HandleFunc("POST /api/article/edit", app.apiEditArticle)
	mux.HandleFunc("POST /api/article/delete", app.apiDeleteArticle)
}

func (app *application) apiUploadArticle(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid article form")
		return
	}
	title, content, err := articleForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	images, err := formImages(r, "imgfiles")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create article")
		return
	}
	defer tx.Rollback()
	result, err := tx.ExecContext(r.Context(), "INSERT INTO articles (userid, title, content, timestamp) VALUES (?, ?, ?, ?)", current.ID, title, content, time.Now().UTC())
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create article")
		return
	}
	articleID, _ := result.LastInsertId()
	if err := saveImages(r.Context(), tx, 3, strconv.FormatInt(articleID, 10), current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create article")
		return
	}
	writeJSON(w, http.StatusCreated, map[string]any{"ok": true, "url": articleURL(articleID)})
}

func (app *application) apiEditArticle(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid article form")
		return
	}
	articleID, err := formInteger(r, "article_id", -1, 1, 1_000_000_000)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	value, err := app.getArticle(r.Context(), int64(articleID))
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !owns(current, value.UserID) {
		writeAPIError(w, http.StatusForbidden, "forbidden")
		return
	}
	title, content, err := articleForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	images, err := formImages(r, "imgfiles")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update article")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), "UPDATE articles SET title = ?, content = ? WHERE id = ?", title, content, articleID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update article")
		return
	}
	if err := saveImages(r.Context(), tx, 3, strconv.Itoa(articleID), current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update article")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": articleURL(int64(articleID))})
}

func (app *application) apiDeleteArticle(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	var body struct{ ArticleID int64 `json:"article_id"` }
	if err := decodeJSONBody(r, &body); err != nil || body.ArticleID < 1 {
		writeAPIError(w, http.StatusBadRequest, "invalid request")
		return
	}
	value, err := app.getArticle(r.Context(), body.ArticleID)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !owns(current, value.UserID) {
		writeAPIError(w, http.StatusForbidden, "forbidden")
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete article")
		return
	}
	defer tx.Rollback()
	postIdent := strconv.FormatInt(body.ArticleID, 10)
	if err := deletePostComments(r.Context(), tx, 3, postIdent); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete comments")
		return
	}
	if _, err := tx.ExecContext(r.Context(), "DELETE FROM articles WHERE id = ?", body.ArticleID); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete article")
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete article")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/"})
}

func articleForm(r *http.Request) (string, string, error) {
	title, err := trimRequired(r.FormValue("articletitle"), "article title", 128)
	if err != nil {
		return "", "", err
	}
	content, err := trimRequired(r.FormValue("article"), "article", 100_000)
	if err != nil {
		return "", "", err
	}
	return title, content, nil
}

func (app *application) getArticle(ctx context.Context, id int64) (*article, error) {
	var value article
	err := app.db.QueryRowContext(ctx, "SELECT id, userid, title, content FROM articles WHERE id = ?", id).Scan(&value.ID, &value.UserID, &value.Title, &value.Content)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, errNotFound
	}
	if err != nil {
		return nil, err
	}
	return &value, nil
}

func articleURL(id int64) string { return "/articles/" + strconv.FormatInt(id, 10) }
