run-checks:
	ruff	format
	js-beautify	-r	static/*.js
	djlint	.\frontend	--reformat
	ruff	check
	djlint	.\frontend

run-docker:
	docker	compose	down
	docker	compose	up	-d	--build
