.PHONY: check demo test

check:
	python3 -m spokenwait validate

demo:
	python3 -m spokenwait demo

test:
	python3 -m unittest discover -s tests -v
