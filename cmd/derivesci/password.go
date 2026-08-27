package main

import (
	"crypto/hmac"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/hex"
	"strconv"
	"strings"

	"golang.org/x/crypto/bcrypt"
	"golang.org/x/crypto/scrypt"
)

func hashPassword(password string) (string, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	return string(hash), err
}

func verifyPassword(stored, password string) bool {
	if strings.HasPrefix(stored, "$2") {
		return bcrypt.CompareHashAndPassword([]byte(stored), []byte(password)) == nil
	}
	parts := strings.Split(stored, "$")
	if len(parts) != 3 {
		return false
	}
	method, salt, expected := parts[0], parts[1], parts[2]
	methodParts := strings.Split(method, ":")
	if len(methodParts) < 2 {
		return false
	}
	switch methodParts[0] {
	case "scrypt":
		if len(methodParts) != 4 {
			return false
		}
		n, nErr := strconv.Atoi(methodParts[1])
		r, rErr := strconv.Atoi(methodParts[2])
		p, pErr := strconv.Atoi(methodParts[3])
		if nErr != nil || rErr != nil || pErr != nil || n <= 1 || r <= 0 || p <= 0 {
			return false
		}
		derived, err := scrypt.Key([]byte(password), []byte(salt), n, r, p, 64)
		if err != nil {
			return false
		}
		encoded := base64.StdEncoding.EncodeToString(derived)
		return subtle.ConstantTimeCompare([]byte(encoded), []byte(expected)) == 1
	case "pbkdf2":
		if len(methodParts) != 3 && len(methodParts) != 4 {
			return false
		}
		digest := methodParts[1]
		iterations, err := strconv.Atoi(methodParts[2])
		if err != nil || iterations <= 0 || digest != "sha256" {
			return false
		}
		derived := pbkdf2SHA256([]byte(password), []byte(salt), iterations, 32)
		return subtle.ConstantTimeCompare([]byte(hex.EncodeToString(derived)), []byte(expected)) == 1
	default:
		return false
	}
}

func pbkdf2SHA256(password, salt []byte, iterations, length int) []byte {
	result := make([]byte, 0, length)
	for block := uint32(1); len(result) < length; block++ {
		mac := hmac.New(sha256.New, password)
		mac.Write(salt)
		mac.Write([]byte{byte(block >> 24), byte(block >> 16), byte(block >> 8), byte(block)})
		u := mac.Sum(nil)
		t := append([]byte(nil), u...)
		for round := 1; round < iterations; round++ {
			mac = hmac.New(sha256.New, password)
			mac.Write(u)
			u = mac.Sum(nil)
			for i := range t {
				t[i] ^= u[i]
			}
		}
		result = append(result, t...)
	}
	return result[:length]
}
