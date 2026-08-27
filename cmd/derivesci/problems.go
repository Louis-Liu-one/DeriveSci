package main

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
)

var problemNumberPattern = regexp.MustCompile(`^[A-Za-z0-9._-]{1,16}$`)

type imageUpload struct {
	Name     string
	MIMEType string
	Data     []byte
}

func (app *application) registerProblemRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /api/tag/rename", app.apiRenameTag)
	mux.HandleFunc("POST /api/prob/search-content", app.apiSearchProblemContent)
	mux.HandleFunc("POST /api/prob/upload", app.apiUploadProblem)
	mux.HandleFunc("POST /api/prob/edit", app.apiEditProblem)
	mux.HandleFunc("POST /api/prob/review", app.apiReviewProblem)
	mux.HandleFunc("POST /api/prob/review-comment", app.apiSaveReviewComment)
	mux.HandleFunc("POST /api/prob/set-official", app.apiSetOfficialProblem)
	mux.HandleFunc("POST /api/prob/delete", app.apiDeleteProblem)
	mux.HandleFunc("POST /api/solution/upload", app.apiUploadSolution)
	mux.HandleFunc("POST /api/solution/edit", app.apiEditSolution)
	mux.HandleFunc("POST /api/solution/delete", app.apiDeleteSolution)
}

func (app *application) apiRenameTag(w http.ResponseWriter, r *http.Request) {
	if _, ok := app.requireAdmin(w, r); !ok {
		return
	}
	var body struct {
		OldTitle string `json:"old_title"`
		NewTitle string `json:"new_title"`
	}
	if err := decodeJSONBody(r, &body); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	oldTitle, err := trimRequired(body.OldTitle, "old_title", 16)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	newTitle, err := trimRequired(body.NewTitle, "new_title", 16)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not rename tag")
		return
	}
	defer tx.Rollback()
	var exists bool
	if err := tx.QueryRowContext(r.Context(), "SELECT EXISTS(SELECT 1 FROM tags WHERE tagtitle = ?)", oldTitle).Scan(&exists); err != nil || !exists {
		writeAPIError(w, http.StatusNotFound, "tag not found")
		return
	}
	if _, err := tx.ExecContext(r.Context(), "INSERT OR IGNORE INTO tags (tagtitle) VALUES (?)", newTitle); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not rename tag")
		return
	}
	if oldTitle != newTitle {
		if _, err := tx.ExecContext(r.Context(), `INSERT OR IGNORE INTO probs_tags (probno, tagtitle) SELECT probno, ? FROM probs_tags WHERE tagtitle = ?`, newTitle, oldTitle); err != nil {
			writeAPIError(w, http.StatusInternalServerError, "could not move tag relations")
			return
		}
		if _, err := tx.ExecContext(r.Context(), "DELETE FROM tags WHERE tagtitle = ?", oldTitle); err != nil {
			writeAPIError(w, http.StatusInternalServerError, "could not remove original tag")
			return
		}
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not rename tag")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/probs/tags/" + pathEscape(newTitle)})
}

func (app *application) apiSearchProblemContent(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Statement  string `json:"statement"`
		ReviewMode bool   `json:"reviewmode"`
		OfTag      bool   `json:"oftag"`
		TagTitle   string `json:"tagtitle"`
	}
	if err := decodeJSONBody(r, &body); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	if len([]rune(body.Statement)) > 1_000 {
		writeAPIError(w, http.StatusBadRequest, "search query is too long")
		return
	}
	reviewMode := body.ReviewMode
	if reviewMode {
		current, err := app.currentUser(r)
		if err != nil || !current.IsAdmin {
			reviewMode = false
		}
	}
	query := "SELECT p.probno FROM probs p"
	args := []any{}
	conditions := []string{"p.statement LIKE ?"}
	args = append(args, "%"+body.Statement+"%")
	if body.OfTag && body.TagTitle != "" {
		query += " JOIN probs_tags pt ON pt.probno = p.probno"
		conditions = append(conditions, "pt.tagtitle = ?")
		args = append(args, body.TagTitle)
	}
	if !reviewMode {
		conditions = append(conditions, "p.review_status = 1")
	}
	query += " WHERE " + strings.Join(conditions, " AND ") + " ORDER BY p.probno"
	rows, err := app.db.QueryContext(r.Context(), query, args...)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not search problems")
		return
	}
	defer rows.Close()
	results := []string{}
	for rows.Next() {
		var number string
		if err := rows.Scan(&number); err != nil {
			writeAPIError(w, http.StatusInternalServerError, "could not read search results")
			return
		}
		results = append(results, number)
	}
	writeJSON(w, http.StatusOK, map[string]any{"results": results})
}

func (app *application) apiUploadProblem(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid problem form")
		return
	}
	input, err := problemForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	images, err := formImages(r, "imgfiles")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	reviewStatus := -1
	isOfficial := false
	if current.IsAdmin {
		reviewStatus = 1
		isOfficial = parseBool(r.FormValue("isofficial"))
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create problem")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), `INSERT INTO probs (probno, probtitle, statement, answer, sourceuid, review_status, isofficial, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, input.Number, input.Title, input.Statement, input.Answers, current.ID, reviewStatus, isOfficial, time.Now().UTC()); err != nil {
		if isUniqueViolation(err) {
			writeAPIError(w, http.StatusConflict, "problem number already exists")
			return
		}
		writeAPIError(w, http.StatusInternalServerError, "could not create problem")
		return
	}
	if err := saveTags(r.Context(), tx, input.Number, input.Tags); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not save tags")
		return
	}
	if err := saveImages(r.Context(), tx, 0, input.Number, current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create problem")
		return
	}
	writeJSON(w, http.StatusCreated, map[string]any{"ok": true, "url": problemURL(input.Number)})
}

func (app *application) apiEditProblem(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid problem form")
		return
	}
	input, err := problemForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	problem, err := app.getProblem(r.Context(), input.Number)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !owns(current, problem.SourceID) {
		writeAPIError(w, http.StatusForbidden, "forbidden")
		return
	}
	images, err := formImages(r, "imgfiles")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update problem")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), "UPDATE probs SET probtitle = ?, statement = ?, answer = ? WHERE probno = ?", input.Title, input.Statement, input.Answers, input.Number); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update problem")
		return
	}
	if err := replaceTags(r.Context(), tx, input.Number, input.Tags); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not save tags")
		return
	}
	if err := saveImages(r.Context(), tx, 0, input.Number, current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update problem")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": problemURL(input.Number)})
}

func (app *application) apiReviewProblem(w http.ResponseWriter, r *http.Request) {
	if _, ok := app.requireAdmin(w, r); !ok {
		return
	}
	var body struct {
		ProblemNumber string  `json:"probno"`
		Accept        bool    `json:"accept"`
		ReviewComment *string `json:"review_comment"`
	}
	if err := decodeJSONBody(r, &body); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid JSON")
		return
	}
	if !validProblemNumber(body.ProblemNumber) {
		writeAPIError(w, http.StatusBadRequest, "invalid problem number")
		return
	}
	if body.ReviewComment != nil && len([]rune(*body.ReviewComment)) > 8_000 {
		writeAPIError(w, http.StatusBadRequest, "review comment is too long")
		return
	}
	status := 0
	if body.Accept {
		status = 1
	}
	result, err := app.db.ExecContext(r.Context(), "UPDATE probs SET review_status = ?, review_comment = COALESCE(?, review_comment) WHERE probno = ?", status, body.ReviewComment, body.ProblemNumber)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not review problem")
		return
	}
	if changed, _ := result.RowsAffected(); changed == 0 {
		writeAPIError(w, http.StatusNotFound, "problem not found")
		return
	}
	url := "/probs/collections/"
	if body.Accept {
		url = problemURL(body.ProblemNumber)
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "accept": body.Accept, "url": url})
}

func (app *application) apiSaveReviewComment(w http.ResponseWriter, r *http.Request) {
	if _, ok := app.requireAdmin(w, r); !ok {
		return
	}
	var body struct {
		ProblemNumber  string `json:"probno"`
		ReviewComment string `json:"review_comment"`
	}
	if err := decodeJSONBody(r, &body); err != nil || !validProblemNumber(body.ProblemNumber) {
		writeAPIError(w, http.StatusBadRequest, "invalid request")
		return
	}
	if len([]rune(body.ReviewComment)) > 8_000 {
		writeAPIError(w, http.StatusBadRequest, "review comment is too long")
		return
	}
	result, err := app.db.ExecContext(r.Context(), "UPDATE probs SET review_comment = ? WHERE probno = ?", body.ReviewComment, body.ProblemNumber)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not save review comment")
		return
	}
	if changed, _ := result.RowsAffected(); changed == 0 {
		writeAPIError(w, http.StatusNotFound, "problem not found")
		return
	}
	writeJSON(w, http.StatusOK, map[string]bool{"ok": true})
}

func (app *application) apiSetOfficialProblem(w http.ResponseWriter, r *http.Request) {
	if _, ok := app.requireAdmin(w, r); !ok {
		return
	}
	var body struct{ ProblemNumber string `json:"probno"` }
	if err := decodeJSONBody(r, &body); err != nil || !validProblemNumber(body.ProblemNumber) {
		writeAPIError(w, http.StatusBadRequest, "invalid request")
		return
	}
	problem, err := app.getProblem(r.Context(), body.ProblemNumber)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	newValue := !problem.IsOfficial
	if _, err := app.db.ExecContext(r.Context(), "UPDATE probs SET isofficial = ? WHERE probno = ?", newValue, body.ProblemNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update problem")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "isofficial": newValue})
}

func (app *application) apiDeleteProblem(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	var body struct{ ProblemNumber string `json:"probno"` }
	if err := decodeJSONBody(r, &body); err != nil || !validProblemNumber(body.ProblemNumber) {
		writeAPIError(w, http.StatusBadRequest, "invalid request")
		return
	}
	problem, err := app.getProblem(r.Context(), body.ProblemNumber)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !owns(current, problem.SourceID) {
		writeAPIError(w, http.StatusForbidden, "forbidden")
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete problem")
		return
	}
	defer tx.Rollback()
	if err := deletePostComments(r.Context(), tx, 0, body.ProblemNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete comments")
		return
	}
	if _, err := tx.ExecContext(r.Context(), "DELETE FROM probs WHERE probno = ?", body.ProblemNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete problem")
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete problem")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": "/probs/collections/"})
}

type problemInput struct {
	Number    string
	Title     string
	Statement string
	Answers   string
	Tags      []string
}

func problemForm(r *http.Request) (problemInput, error) {
	number := strings.TrimSpace(r.FormValue("probno"))
	if !validProblemNumber(number) {
		return problemInput{}, errors.New("problem number must contain 1 to 16 letters, digits, dots, underscores, or hyphens")
	}
	title, err := trimRequired(r.FormValue("probtitle"), "problem title", 64)
	if err != nil {
		return problemInput{}, err
	}
	statement, err := trimRequired(r.FormValue("statement"), "problem statement", 100_000)
	if err != nil {
		return problemInput{}, err
	}
	answers := strings.TrimSpace(r.FormValue("answers"))
	if answers != "" && !json.Valid([]byte(answers)) {
		return problemInput{}, errors.New("answers must be valid JSON")
	}
	tags, err := parseTags(r.FormValue("tags"))
	if err != nil {
		return problemInput{}, err
	}
	return problemInput{Number: number, Title: title, Statement: statement, Answers: answers, Tags: tags}, nil
}

func validProblemNumber(value string) bool { return problemNumberPattern.MatchString(value) }

func parseTags(value string) ([]string, error) {
	if strings.TrimSpace(value) == "" {
		return nil, nil
	}
	var raw []string
	if err := json.Unmarshal([]byte(value), &raw); err != nil {
		return nil, errors.New("tags must be a JSON list")
	}
	unique := make(map[string]struct{}, len(raw))
	for _, tag := range raw {
		tag, err := trimRequired(tag, "tag", 16)
		if err != nil {
			return nil, err
		}
		unique[tag] = struct{}{}
	}
	result := make([]string, 0, len(unique))
	for tag := range unique {
		result = append(result, tag)
	}
	sort.Strings(result)
	return result, nil
}

func formImages(r *http.Request, field string) ([]imageUpload, error) {
	if r.MultipartForm == nil || r.MultipartForm.File == nil {
		return nil, nil
	}
	headers := r.MultipartForm.File[field]
	if len(headers) > 10 {
		return nil, errors.New("a post may contain at most 10 images")
	}
	result := make([]imageUpload, 0, len(headers))
	names := map[string]struct{}{}
	for _, header := range headers {
		name := filepath.Base(header.Filename)
		if name != header.Filename || name == "." || name == "" || len([]rune(name)) > 64 {
			return nil, errors.New("invalid image filename")
		}
		if _, exists := names[name]; exists {
			return nil, errors.New("image filenames must be unique")
		}
		names[name] = struct{}{}
		file, err := header.Open()
		if err != nil {
			return nil, errors.New("could not read image")
		}
		data, mimeType, imageErr := readValidatedImage(file)
		file.Close()
		if imageErr != nil {
			return nil, imageErr
		}
		result = append(result, imageUpload{Name: name, MIMEType: mimeType, Data: data})
	}
	return result, nil
}

func (app *application) getProblem(ctx context.Context, number string) (*problem, error) {
	var value problem
	err := app.db.QueryRowContext(ctx, `SELECT probno, probtitle, statement, COALESCE(answer, ''), sourceuid, review_status, isofficial, COALESCE(review_comment, '') FROM probs WHERE probno = ?`, number).Scan(&value.Number, &value.Title, &value.Statement, &value.Answer, &value.SourceID, &value.ReviewStatus, &value.IsOfficial, &value.ReviewComment)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, errNotFound
	}
	if err != nil {
		return nil, err
	}
	return &value, nil
}

func owns(current *user, owner sql.NullInt64) bool {
	return current.IsAdmin || (owner.Valid && owner.Int64 == current.ID)
}

func saveTags(ctx context.Context, tx *sql.Tx, problemNumber string, tags []string) error {
	for _, tag := range tags {
		if _, err := tx.ExecContext(ctx, "INSERT OR IGNORE INTO tags (tagtitle) VALUES (?)", tag); err != nil {
			return err
		}
		if _, err := tx.ExecContext(ctx, "INSERT INTO probs_tags (probno, tagtitle) VALUES (?, ?)", problemNumber, tag); err != nil {
			return err
		}
	}
	return nil
}

func replaceTags(ctx context.Context, tx *sql.Tx, problemNumber string, tags []string) error {
	if _, err := tx.ExecContext(ctx, "DELETE FROM probs_tags WHERE probno = ?", problemNumber); err != nil {
		return err
	}
	return saveTags(ctx, tx, problemNumber, tags)
}

func saveImages(ctx context.Context, tx *sql.Tx, postType int, postIdent string, userID int64, images []imageUpload) error {
	for _, image := range images {
		_, err := tx.ExecContext(ctx, `INSERT INTO images (post_type, post_ident, name, uid, size, mimetype, data, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)`, postType, postIdent, image.Name, userID, len(image.Data), image.MIMEType, image.Data, time.Now().UTC())
		if isUniqueViolation(err) {
			return fmt.Errorf("image filename already exists")
		}
		if err != nil {
			return err
		}
	}
	return nil
}

func deletePostComments(ctx context.Context, tx *sql.Tx, postType int, postIdent string) error {
	_, err := tx.ExecContext(ctx, "DELETE FROM comments WHERE post_type = ? AND post_ident = ?", postType, postIdent)
	return err
}

func problemURL(number string) string { return "/probs/collections/" + pathEscape(number) }

func pathEscape(value string) string {
	return strings.ReplaceAll(url.PathEscape(value), "+", "%20")
}

func pathID(r *http.Request, name string) (int64, error) {
	return strconv.ParseInt(r.PathValue(name), 10, 64)
}
