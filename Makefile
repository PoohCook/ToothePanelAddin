

lint:
	pycodestyle --config .pycodestyle.cfg ./ 

test:
	src/blogger/beaconssh.py -t
	rm -rf tmp_files
