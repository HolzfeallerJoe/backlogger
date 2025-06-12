run-checks:
	ruff	format
	ruff	check
	djlint	.\frontend\	--reformat
	djlint	.\frontend\

run-docker:
	docker	compose	down
	docker	compose	up	-d	--build
