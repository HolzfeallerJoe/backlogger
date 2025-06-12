run-sqlite:
	set DATABASE=sqlite && fastapi dev .\backend\backend.py

run-postgres:
	set DATABASE=postgres && fastapi dev .\backend\backend.py

