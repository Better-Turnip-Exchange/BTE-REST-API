venv:
	python3 -m venv venv
	venv/bin/pip3 install pip-tools

requirements.txt: requirements.in ## create requirements
	venv/bin/pip-compile -o requirements.txt \
	--no-header \
	--no-index \
	--no-emit-trusted-host \
	requirements.in


build: venv ## setup environment
	venv/bin/pip-sync requirements.txt

run:
	source venv/bin/activate && uvicorn server.main:app --host 0.0.0.0 --port 8080 --reload

dev-run:
	source venv/bin/activate && DEBUG=true uvicorn server.main:app --reload

clean:
	rm -rf ${CLEANUP} && rm -rf venv