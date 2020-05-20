venv:
	python3 -m venv venv
	venv/bin/pip3 install pip-tools

requirements.txt: requirements.in ## create requirements
	venv/bin/pip-compile -o requirements.txt \
	--no-header \
	--no-index \
	--no-emit-trusted-host \
	requirements.in

requirements-dev.txt: requirements-dev.in ## create requirements
	venv/bin/pip-compile -o requirements-dev.txt \
	--no-header \
	--no-index \
	--no-emit-trusted-host \
	requirements-dev.in

build: venv ## setup environment
	venv/bin/pip-sync requirements.txt

dev: venv ## setup dev environment
	venv/bin/pip-sync requirements-dev.txt

run:
	source venv/bin/activate && uvicorn server.main:app --host 0.0.0.0 --port 8080 --reload

dev-run:
	source venv/bin/activate && DEBUG=true uvicorn server.main:app --reload

clean:
	rm -rf .pytest_cache \
	&& rm -rf server/__pycache__ \
	&& rm -rf server/.pytest_cache\
	&& rm -rf server/tests/__pycache__\
	&& rm -rf server/tests/.pytest_cache\
	&& rm -rf venv


test: dev
	source venv/bin/activate; pytest --disable-pytest-warnings; \
	make clean