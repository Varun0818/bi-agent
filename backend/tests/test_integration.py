"""
Integration checks against a running FastAPI backend (httpx, no pytest).

Run: make test   (with `make dev-back` or docker backend on port 8000)
"""

import sys

import httpx

BASE = "http://localhost:8000"


def main() -> None:
    passed = 0
    total = 8
    session_id: str | None = None
    first_query_id: str | None = None

    with httpx.Client(base_url=BASE, timeout=180.0, follow_redirects=True) as client:
        # 1. GET / → status ok
        try:
            r1 = client.get("/")
            d1 = r1.json()
            ok1 = r1.status_code == 200 and d1.get("status") == "ok"
        except Exception as e:
            ok1 = False
            d1 = {"error": str(e)}
        print(f"{'✅' if ok1 else '❌'} 1 GET / → status ok")
        passed += int(ok1)

        # 2. GET /api/v1/schema → tables key, len>=5
        try:
            r2 = client.get("/api/v1/schema/")
            d2 = r2.json()
            tables = d2.get("tables") or {}
            ok2 = r2.status_code == 200 and isinstance(tables, dict) and len(tables) >= 5
        except Exception as e:
            ok2 = False
            d2 = {"error": str(e)}
        print(f"{'✅' if ok2 else '❌'} 2 GET /api/v1/schema → tables len>=5")
        passed += int(ok2)

        # 3. POST /api/v1/sessions → session_id
        try:
            r3 = client.post("/api/v1/sessions/", json={"session_name": "integration"})
            d3 = r3.json()
            session_id = d3.get("session_id")
            ok3 = r3.status_code == 200 and bool(session_id)
        except Exception as e:
            ok3 = False
            d3 = {"error": str(e)}
        print(f"{'✅' if ok3 else '❌'} 3 POST /api/v1/sessions → session_id")
        passed += int(ok3)

        # 4. POST /api/v1/chat/query — data question
        try:
            assert session_id
            r4 = client.post(
                "/api/v1/chat/query",
                json={
                    "user_query": "How many orders total?",
                    "session_id": session_id,
                },
            )
            d4 = r4.json()
            first_query_id = d4.get("query_id")
            trace4 = d4.get("trace") or []
            ok4 = (
                r4.status_code == 200
                and d4.get("success") is True
                and int(d4.get("row_count") or 0) > 0
                and bool(d4.get("generated_sql"))
                and len(trace4) >= 4
            )
        except Exception as e:
            ok4 = False
            d4 = {"error": str(e)}
        print(
            f"{'✅' if ok4 else '❌'} 4 POST /api/v1/chat/query (data) → "
            "success, row_count, sql, trace"
        )
        passed += int(ok4)

        # 5. GET /api/v1/history?session_id=
        try:
            assert session_id
            r5 = client.get(
                "/api/v1/history/",
                params={"session_id": session_id},
            )
            h5 = r5.json()
            ok5 = r5.status_code == 200 and isinstance(h5, list) and len(h5) >= 1
        except Exception as e:
            ok5 = False
            h5 = {"error": str(e)}
        print(f"{'✅' if ok5 else '❌'} 5 GET /api/v1/history → len>=1")
        passed += int(ok5)

        # 6. GET /api/v1/traces/{query_id}
        try:
            assert first_query_id
            r6 = client.get(f"/api/v1/traces/{first_query_id}")
            t6 = r6.json()
            ok6 = r6.status_code == 200 and isinstance(t6, list) and len(t6) >= 4
        except Exception as e:
            ok6 = False
            t6 = {"error": str(e)}
        print(f"{'✅' if ok6 else '❌'} 6 GET /api/v1/traces/<query_id> → len>=4")
        passed += int(ok6)

        # 7. POST chitchat
        try:
            assert session_id
            r7 = client.post(
                "/api/v1/chat/query",
                json={"user_query": "Hello!", "session_id": session_id},
            )
            d7 = r7.json()
            ok7 = (
                r7.status_code == 200
                and d7.get("intent") == "chitchat"
                and d7.get("generated_sql") == ""
            )
        except Exception as e:
            ok7 = False
            d7 = {"error": str(e)}
        print(f"{'✅' if ok7 else '❌'} 7 POST chitchat → intent, empty sql")
        passed += int(ok7)

        # 8. Second data query — multi-turn session (history grows; full trace on server)
        try:
            assert session_id
            r8 = client.post(
                "/api/v1/chat/query",
                json={
                    "user_query": "How many products are in the Food category?",
                    "session_id": session_id,
                },
            )
            d8 = r8.json()
            trace8 = d8.get("trace") or []
            r8h = client.get(
                "/api/v1/history/",
                params={"session_id": session_id},
            )
            hist8 = r8h.json()
            ok8 = (
                r8.status_code == 200
                and r8h.status_code == 200
                and d8.get("success") is True
                and len(trace8) >= 4
                and isinstance(hist8, list)
                and len(hist8) >= 3
            )
        except Exception as e:
            ok8 = False
            d8 = {"error": str(e)}
        print(
            f"{'✅' if ok8 else '❌'} 8 second data query → trace depth + history>=3 "
            "(multi-turn session)"
        )
        passed += int(ok8)

    print(f"{passed}/{total} tests passed")
    if passed < total:
        sys.exit(1)


if __name__ == "__main__":
    main()
