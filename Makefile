run_main:
	python3 -m wumpus.main
install:
	pip install -r requirements.txt
freeze-pip:
	pip freeze --local > requirements.txt
