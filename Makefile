.PHONY: install build serve clean

install:
	cd frontend && npm install
	uv sync

build:
	cd frontend && npm run build

serve: build
	uv run python main.py

clean:
	rm -rf frontend/dist frontend/node_modules
