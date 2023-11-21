# Rule to run pytest with coverage and remove test_database.sqlite
test:
	pytest -vv --cov=../src/theThing .
	rm -f ../src/*.sqlite

clean:
	rm -f ../src/*.sqlite
	rm -f test.db