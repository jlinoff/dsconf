.PHONY: all clean test
all: test

clean:
	@find .. -name '*~' -delete

test: ../dsconf.py ./gends.py
	@./test.sh | grep ^test:

test-verbose: ../dsconf.py ./gends.py
	@./test.sh
