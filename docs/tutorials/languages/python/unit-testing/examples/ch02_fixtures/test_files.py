import json


def test_json_save(tmp_path):
    # Arrange
    data = {"name": "Test"}
    file_path = tmp_path / "data.json"

    # Act
    with open(file_path, "w") as f:
        json.dump(data, f)

    # Assert
    assert file_path.exists()
    with open(file_path) as f:
        assert json.load(f) == data
