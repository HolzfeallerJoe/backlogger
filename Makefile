run-sqlite:
	set DATABASE=sqlite && fastapi dev backend.py

run-postgres:
	set DATABASE=postgres && fastapi dev backend.py

