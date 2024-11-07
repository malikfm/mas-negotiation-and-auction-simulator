.PHONY: run
run:
	poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

.PHONY: clean
clean:
	rm -rf requirements.txt

.PHONY: requirements
requirements:
	poetry export --without-hashes --format=requirements.txt > requirements.txt

.PHONY: bootstrap
bootstrap:
	poetry run python bootstrap.py

.PHONY: fmt
fmt:
	poetry run isort .
	poetry run black .

.PHONY: deploy
deploy: clean requirements bootstrap
	vercel
