all:
	python3 AdminPanel.py

venv:
	source venv/bin/activate

get:
	sudo apt install python3-venv python3-pip

update:
	sudo apt update

build-venv:
	python3 -m venv venv

get-pip:
	pip install discord.py

