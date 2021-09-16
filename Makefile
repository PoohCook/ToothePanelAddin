
.PHONY: lint test

lint:
	pycodestyle --config .pycodestyle.cfg ./ 

test: 
	./PanelTest.py