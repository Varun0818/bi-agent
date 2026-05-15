.PHONY: setup dev-back dev-front docker eval test clean

setup:
	cd backend && pip install -r requirements.txt && python db/init_db.py

dev-back:
	cd backend && uvicorn main:app --reload --port 8000

dev-front:
	cd frontend && npm run dev

docker:
	docker-compose up --build

eval:
	cd backend && python evals/run_eval.py --run-name latest

test:
	cd backend && python tests/test_integration.py

clean:
	docker-compose down -v
