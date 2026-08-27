package main

import (
	"context"
	"database/sql"
	"errors"
	"net/http"
	"strconv"
	"strings"
	"time"
)

func (app *application) apiUploadSolution(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid solution form")
		return
	}
	problemNumber, title, content, err := solutionForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	problem, err := app.getProblem(r.Context(), problemNumber)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !canViewProblem(current, problem) {
		writeAPIError(w, http.StatusNotFound, "problem not found")
		return
	}
	images, err := formImages(r, "imgfiles")
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	tx, err := app.db.BeginTx(r.Context(), nil)
	if err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create solution")
		return
	}
	defer tx.Rollback()
	var solutionNumber int
	if err := tx.QueryRowContext(r.Context(), "SELECT COALESCE(MAX(solno), -1) + 1 FROM solutions WHERE probno = ?", problemNumber).Scan(&solutionNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not number solution")
		return
	}
	if _, err := tx.ExecContext(r.Context(), `INSERT INTO solutions (probno, solno, userid, title, content, timestamp) VALUES (?, ?, ?, ?, ?, ?)`, problemNumber, solutionNumber, current.ID, title, content, time.Now().UTC()); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create solution")
		return
	}
	postIdent := solutionPostIdent(problemNumber, solutionNumber)
	if err := saveImages(r.Context(), tx, 1, postIdent, current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not create solution")
		return
	}
	writeJSON(w, http.StatusCreated, map[string]any{"ok": true, "url": solutionURL(problemNumber, solutionNumber)})
}

func (app *application) apiEditSolution(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	if err := r.ParseMultipartForm(maxRequestBody); err != nil {
		writeAPIError(w, http.StatusBadRequest, "invalid solution form")
		return
	}
	problemNumber, title, content, err := solutionForm(r)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	solutionNumber, err := formInteger(r, "solno", -1, 0, 1_000_000)
	if err != nil {
		writeAPIError(w, http.StatusBadRequest, err.Error())
		return
	}
	value, err := app.getSolution(r.Context(), problemNumber, solutionNumber)
	if err != nil {
		asHTTPError(w, err)
		return
	}
	if !owns(current, value.UserID) {
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
		writeAPIError(w, http.StatusInternalServerError, "could not update solution")
		return
	}
	defer tx.Rollback()
	if _, err := tx.ExecContext(r.Context(), "UPDATE solutions SET title = ?, content = ? WHERE probno = ? AND solno = ?", title, content, problemNumber, solutionNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update solution")
		return
	}
	if err := saveImages(r.Context(), tx, 1, solutionPostIdent(problemNumber, solutionNumber), current.ID, images); err != nil {
		asHTTPError(w, err)
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not update solution")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": solutionURL(problemNumber, solutionNumber)})
}

func (app *application) apiDeleteSolution(w http.ResponseWriter, r *http.Request) {
	current, ok := app.requireUser(w, r)
	if !ok {
		return
	}
	var body struct {
		ProblemNumber string `json:"probno"`
		SolutionNumber int `json:"solno"`
	}
	if err := decodeJSONBody(r, &body); err != nil || !validProblemNumber(body.ProblemNumber) || body.SolutionNumber < 0 {
		writeAPIError(w, http.StatusBadRequest, "invalid request")
		return
	}
	value, err := app.getSolution(r.Context(), body.ProblemNumber, body.SolutionNumber)
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
		writeAPIError(w, http.StatusInternalServerError, "could not delete solution")
		return
	}
	defer tx.Rollback()
	postIdent := solutionPostIdent(body.ProblemNumber, body.SolutionNumber)
	if err := deletePostComments(r.Context(), tx, 1, postIdent); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete comments")
		return
	}
	if _, err := tx.ExecContext(r.Context(), "DELETE FROM solutions WHERE probno = ? AND solno = ?", body.ProblemNumber, body.SolutionNumber); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete solution")
		return
	}
	if err := tx.Commit(); err != nil {
		writeAPIError(w, http.StatusInternalServerError, "could not delete solution")
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{"ok": true, "url": problemURL(body.ProblemNumber)})
}

func solutionForm(r *http.Request) (string, string, string, error) {
	problemNumber := strings.TrimSpace(r.FormValue("probno"))
	if !validProblemNumber(problemNumber) {
		return "", "", "", errors.New("invalid problem number")
	}
	title, err := trimRequired(r.FormValue("soltitle"), "solution title", 128)
	if err != nil {
		return "", "", "", err
	}
	content, err := trimRequired(r.FormValue("solution"), "solution", 100_000)
	if err != nil {
		return "", "", "", err
	}
	return problemNumber, title, content, nil
}

func (app *application) getSolution(ctx context.Context, problemNumber string, solutionNumber int) (*solution, error) {
	var value solution
	err := app.db.QueryRowContext(ctx, `SELECT probno, solno, userid, title, content FROM solutions WHERE probno = ? AND solno = ?`, problemNumber, solutionNumber).Scan(&value.ProblemNumber, &value.Number, &value.UserID, &value.Title, &value.Content)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, errNotFound
	}
	if err != nil {
		return nil, err
	}
	return &value, nil
}

func canViewProblem(current *user, value *problem) bool {
	return value.ReviewStatus == 1 || (current != nil && owns(current, value.SourceID))
}

func solutionPostIdent(problemNumber string, solutionNumber int) string {
	return problemNumber + "," + strconv.Itoa(solutionNumber)
}

func solutionURL(problemNumber string, solutionNumber int) string {
	return problemURL(problemNumber) + "/solutions/" + strconv.Itoa(solutionNumber)
}
