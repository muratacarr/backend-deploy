# Simple Makefile for FastAPI Backend

.PHONY: run stop kill-port

# Kill process on port 8000
kill-port:
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Stop server
stop: kill-port

# Start server (kill port first, then start)
run: kill-port
	@python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000