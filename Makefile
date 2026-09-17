install:
	pip install -r requirements.txt

pipeline:
	python src/pipeline.py

validate:
	python src/validation.py

test:
	pytest tests/test_aggregation.py

dashboard:
	streamlit run dashboard/app.py