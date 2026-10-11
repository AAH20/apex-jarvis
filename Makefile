.PHONY: test benchmark lint clean

test:
	python3 -m unittest discover -s tests -p "test_*.py"

benchmark:
	python3 benchmarks/run_master_test.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
