package main

import (
	"context"
	"crypto/rand"
	"database/sql"
	_ "embed"
	"encoding/json"
	"encoding/base64"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/gorilla/csrf"
	"github.com/gorilla/securecookie"
	_ "modernc.org/sqlite"
)

const defaultAddress = ":8080"

//go:embed web/page.html
var pageTemplate string

type config struct {
	address      string
	databaseDSN  string
	staticDir    string
	cookieSecure bool
	hashKey      []byte
	blockKey     []byte
}

func main() {
	cfg, err := loadConfig()
	if err != nil {
		log.Fatal(err)
	}

	db, err := sql.Open("sqlite", cfg.databaseDSN)
	if err != nil {
		log.Fatalf("open database: %v", err)
	}
	defer db.Close()
	if err := initializeDatabase(db); err != nil {
		log.Fatalf("initialize database: %v", err)
	}

	app := newApplication(db, cfg)
	server := &http.Server{
		Addr:              cfg.address,
		Handler:           app.routes(),
		ReadHeaderTimeout: 10 * time.Second,
		ReadTimeout:       20 * time.Second,
		WriteTimeout:      30 * time.Second,
		IdleTimeout:       60 * time.Second,
	}

	go func() {
		log.Printf("DeriveSci Go backend listening on http://localhost%s", cfg.address)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("serve: %v", err)
		}
	}()

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt, syscall.SIGTERM)
	<-signals
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := server.Shutdown(ctx); err != nil {
		log.Printf("shutdown: %v", err)
	}
}

func loadConfig() (config, error) {
	staticDir := envOr("STATIC_DIR", "static")
	databaseDSN := envOr("DATABASE_DSN", "instance/test.db")
	if !strings.HasPrefix(databaseDSN, "file:") && databaseDSN != ":memory:" {
		databaseDSN = "file:" + filepath.ToSlash(databaseDSN) + "?_pragma=foreign_keys(1)&_pragma=busy_timeout(5000)"
	}

	hashKey, err := configKey("SESSION_HASH_KEY", 32)
	if err != nil {
		return config{}, err
	}
	blockKey, err := configKey("SESSION_BLOCK_KEY", 32)
	if err != nil {
		return config{}, err
	}
	return config{
		address:      envOr("APP_ADDR", defaultAddress),
		databaseDSN:  databaseDSN,
		staticDir:    staticDir,
		cookieSecure: envOr("COOKIE_SECURE", "false") == "true",
		hashKey:      hashKey,
		blockKey:     blockKey,
	}, nil
}

func configKey(name string, size int) ([]byte, error) {
	if value := os.Getenv(name); value != "" {
		key, err := base64.RawURLEncoding.DecodeString(value)
		if err != nil || len(key) < 32 {
			return nil, fmt.Errorf("%s must be a base64url-encoded key of at least 32 bytes", name)
		}
		return key, nil
	}
	key := make([]byte, size)
	if _, err := rand.Read(key); err != nil {
		return nil, fmt.Errorf("generate %s: %w", name, err)
	}
	log.Printf("%s is not configured; generated a temporary key for this process", name)
	return key, nil
}

func envOr(name, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}

func initializeDatabase(db *sql.DB) error {
	_, err := db.Exec(schema)
	return err
}

var schema = `
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
  uid INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  gender INTEGER NOT NULL DEFAULT 0,
  password TEXT NOT NULL,
  introduction TEXT,
  avatar BLOB,
  avmimetype TEXT,
  avlastmodified DATETIME DEFAULT CURRENT_TIMESTAMP,
  cmtlastvisit DATETIME DEFAULT CURRENT_TIMESTAMP,
  isadmin BOOLEAN NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tags (
  tagtitle TEXT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS probs (
  probno TEXT PRIMARY KEY,
  probtitle TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  statement TEXT NOT NULL,
  answer TEXT,
  sourceuid INTEGER REFERENCES users(uid) ON DELETE SET NULL,
  review_status INTEGER NOT NULL DEFAULT -1,
  isofficial BOOLEAN NOT NULL DEFAULT 0,
  review_comment TEXT
);
CREATE TABLE IF NOT EXISTS probs_tags (
  probno TEXT NOT NULL REFERENCES probs(probno) ON DELETE CASCADE,
  tagtitle TEXT NOT NULL REFERENCES tags(tagtitle) ON DELETE CASCADE,
  PRIMARY KEY (probno, tagtitle)
);
CREATE TABLE IF NOT EXISTS submissions (
  submitid INTEGER PRIMARY KEY AUTOINCREMENT,
  probno TEXT NOT NULL REFERENCES probs(probno) ON DELETE CASCADE,
  userid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
  answer TEXT NOT NULL,
  ispassed BOOLEAN,
  score INTEGER,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS solutions (
  probno TEXT NOT NULL REFERENCES probs(probno) ON DELETE CASCADE,
  solno INTEGER NOT NULL,
  userid INTEGER REFERENCES users(uid) ON DELETE SET NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (probno, solno)
);
CREATE TABLE IF NOT EXISTS articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  userid INTEGER REFERENCES users(uid) ON DELETE SET NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS images (
  post_type INTEGER NOT NULL,
  post_ident TEXT NOT NULL,
  name TEXT NOT NULL,
  uid INTEGER REFERENCES users(uid) ON DELETE SET NULL,
  size INTEGER NOT NULL,
  mimetype TEXT NOT NULL,
  data BLOB NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (post_type, post_ident, name)
);
CREATE TABLE IF NOT EXISTS comments (
  cmtid INTEGER PRIMARY KEY AUTOINCREMENT,
  uid INTEGER REFERENCES users(uid) ON DELETE SET NULL,
  content TEXT NOT NULL,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  replyto_id INTEGER REFERENCES comments(cmtid) ON DELETE SET NULL,
  post_type INTEGER NOT NULL,
  post_ident TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_chats (
  uid_receiver INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
  uid_sender INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
  lastvisit DATETIME DEFAULT '1000-01-01 00:00:00',
  PRIMARY KEY (uid_receiver, uid_sender)
);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_type, post_ident, timestamp);
CREATE INDEX IF NOT EXISTS idx_submissions_user_prob ON submissions(userid, probno);
`

type application struct {
	db      *sql.DB
	cookies *securecookie.SecureCookie
	config  config
	csrf    func(http.Handler) http.Handler
}

func newApplication(db *sql.DB, cfg config) *application {
	csrfProtection := csrf.Protect(
		cfg.hashKey,
		csrf.Secure(cfg.cookieSecure),
		csrf.HttpOnly(true),
		csrf.SameSite(csrf.SameSiteLaxMode),
		csrf.Path("/"),
		csrf.ErrorHandler(http.HandlerFunc(csrfFailure)),
	)
	return &application{
		db:      db,
		cookies: securecookie.New(cfg.hashKey, cfg.blockKey),
		config:  cfg,
		csrf:    csrfProtection,
	}
}

func (app *application) routes() http.Handler {
	mux := http.NewServeMux()
	app.registerPageRoutes(mux)
	app.registerAPIRoutes(mux)
	mux.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir(app.config.staticDir))))
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) { writeJSON(w, http.StatusOK, map[string]bool{"ok": true}) })
	return app.withSecurity(app.csrf(mux))
}

func (app *application) withSecurity(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "same-origin")
		w.Header().Set("X-Frame-Options", "SAMEORIGIN")
		w.Header().Set("Content-Security-Policy", "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https:; script-src 'self' 'unsafe-inline' https:; font-src 'self' https:; connect-src 'self'")
		if strings.HasPrefix(r.URL.Path, "/api/") && unsafeMethod(r.Method) {
			if !sameOriginRequest(r) {
				writeAPIError(w, http.StatusForbidden, "cross-origin request rejected")
				return
			}
			next.ServeHTTP(w, csrf.UnsafeSkipCheck(r))
			return
		}
		next.ServeHTTP(w, r)
	})
}

func unsafeMethod(method string) bool {
	return method != http.MethodGet && method != http.MethodHead && method != http.MethodOptions
}

func sameOriginRequest(r *http.Request) bool {
	if site := r.Header.Get("Sec-Fetch-Site"); site != "" && site != "same-origin" && site != "same-site" && site != "none" {
		return false
	}
	for _, header := range []string{"Origin", "Referer"} {
		value := r.Header.Get(header)
		if value == "" {
			continue
		}
		parsed, err := url.Parse(value)
		if err != nil || parsed.Host != r.Host || (parsed.Scheme != "http" && parsed.Scheme != "https") {
			return false
		}
	}
	return true
}

func csrfFailure(w http.ResponseWriter, r *http.Request) {
	if strings.HasPrefix(r.URL.Path, "/api/") {
		writeAPIError(w, http.StatusForbidden, "invalid CSRF token")
		return
	}
	http.Error(w, "invalid CSRF token", http.StatusForbidden)
}

func writeJSON(w http.ResponseWriter, status int, value any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(value)
}
