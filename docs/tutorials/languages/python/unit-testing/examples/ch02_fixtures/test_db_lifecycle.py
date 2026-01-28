def test_db_is_connected(db):
    # 'db' fixture is automatically created before this test
    assert db.status == "connected"
    # When test ends, db.close() is called automatically
