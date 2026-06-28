"""Temp test to debug sqlcipher3 + initialize_database."""

from __future__ import annotations

import tempfile
from pathlib import Path

import sqlcipher3


def test_initialize_sqlcipher() -> None:
    from app.src.db import initialize_database

    p = Path(tempfile.gettempdir()) / "testconf_init.sqlite3"
    if p.exists():
        p.unlink()
    conn = sqlcipher3.connect(str(p), check_same_thread=False)
    conn.execute("PRAGMA key = 'secret123'")
    initialize_database(conn)
    conn.execute("CREATE TABLE IF NOT EXISTS t(a)")
    conn.execute("INSERT INTO t VALUES ('hello')")
    conn.commit()
    conn.close()

    conn2 = sqlcipher3.connect(str(p), check_same_thread=False)
    conn2.execute("PRAGMA key = 'secret123'")
    print(list(conn2.execute("SELECT * FROM t")))
    conn2.close()


def test_connect_workspace_data_db() -> None:
    from app.src.db import connect_workspace_data_db, get_database_path, get_workspace_database_path
    import os

    db_path = Path(tempfile.gettempdir()) / "main_test.sqlite3"
    os.environ["FABERLOOM_DB_PATH"] = str(db_path)
    if db_path.exists():
        db_path.unlink()
    data_path = get_workspace_database_path("ws_abc", db_path)
    if data_path.exists():
        data_path.unlink()

    conn = connect_workspace_data_db("ws_abc", "secret123", main_path=db_path)
    print("opened", data_path)
    conn.execute("CREATE TABLE IF NOT EXISTS t(a)")
    conn.execute("INSERT INTO t VALUES ('hello')")
    conn.commit()
    conn.close()

    conn2 = connect_workspace_data_db("ws_abc", "secret123", main_path=db_path)
    print(list(conn2.execute("SELECT * FROM t")))
    conn2.close()
