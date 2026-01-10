import pytest
from pydantic import ValidationError

from engn.data.models import TypeDef, Property
from engn.data.dynamic import gen_pydantic_models


def test_numeric_validation():
    """Test numeric validation constraints."""
    prop = Property(name="age", type="int", gt=0, le=120, multiple_of=2)
    type_def = TypeDef(name="Person", properties=[prop])

    models = gen_pydantic_models([type_def])
    Person = models["Person"]

    # Valid case
    p = Person(age=30)
    assert getattr(p, "age") == 30

    # Invalid: not greater than 0
    with pytest.raises(ValidationError) as exc:
        Person(age=0)
    assert "Input should be greater than 0" in str(exc.value)

    # Invalid: greater than 120
    # Note: 121 is not a multiple of 2, so it might fail that check first or as well.
    # To reliably test 'le', we should use a value that IS a multiple of 2 but > 120.
    with pytest.raises(ValidationError) as exc:
        Person(age=122)
    assert "Input should be less than or equal to 120" in str(exc.value)

    # Invalid: not multiple of 2
    with pytest.raises(ValidationError) as exc:
        Person(age=31)
    assert "Input should be a multiple of 2" in str(exc.value)


def test_numeric_validation_extended():
    """Test extended numeric validation constraints (ge, lt, exclude, whole_number)."""
    prop = Property(
        name="score",
        type="float",
        ge=0,
        lt=100,
        exclude=[50.0, 50.5],
        whole_number=True,
    )
    type_def = TypeDef(name="ScoreBoard", properties=[prop])

    models = gen_pydantic_models([type_def])
    ScoreBoard = models["ScoreBoard"]

    # Valid case
    s = ScoreBoard(score=10.0)
    assert getattr(s, "score") == 10.0

    # Invalid: less than 0 (ge)
    with pytest.raises(ValidationError) as exc:
        ScoreBoard(score=-1.0)
    assert "Input should be greater than or equal to 0" in str(exc.value)

    # Invalid: equal to 100 (lt)
    with pytest.raises(ValidationError) as exc:
        ScoreBoard(score=100.0)
    assert "Input should be less than 100" in str(exc.value)

    # Invalid: excluded value
    with pytest.raises(ValidationError) as exc:
        ScoreBoard(score=50.0)
    assert "Value is excluded" in str(exc.value)

    # Invalid: not a whole number
    with pytest.raises(ValidationError) as exc:
        ScoreBoard(score=10.5)
    assert "Value must be a whole number" in str(exc.value)


def test_string_validation():
    """Test string validation constraints."""
    prop = Property(name="code", type="str", str_min=3, str_max=5, str_regex="^[A-Z]+$")
    type_def = TypeDef(name="Product", properties=[prop])

    models = gen_pydantic_models([type_def])
    Product = models["Product"]

    # Valid case
    p = Product(code="ABC")
    assert getattr(p, "code") == "ABC"

    # Invalid: too short
    with pytest.raises(ValidationError) as exc:
        Product(code="AB")
    assert "String should have at least 3 characters" in str(exc.value)

    # Invalid: too long
    with pytest.raises(ValidationError) as exc:
        Product(code="ABCDEF")
    assert "String should have at most 5 characters" in str(exc.value)

    # Invalid: regex mismatch
    with pytest.raises(ValidationError) as exc:
        Product(code="abc")
    assert "String should match pattern '^[A-Z]+$'" in str(exc.value)


def test_list_validation():
    """Test list validation constraints."""
    prop = Property(name="tags", type="list[str]", list_min=1, list_max=3)
    type_def = TypeDef(name="Post", properties=[prop])

    models = gen_pydantic_models([type_def])
    Post = models["Post"]

    # Valid case
    p = Post(tags=["news"])
    assert getattr(p, "tags") == ["news"]

    # Invalid: too few items
    with pytest.raises(ValidationError) as exc:
        Post(tags=[])
    assert "List should have at least 1 item" in str(exc.value)


def test_datetime_validation():
    """Test date/time validation constraints."""
    import datetime

    limit_before = datetime.datetime(2025, 1, 1)
    limit_after = datetime.datetime(2023, 1, 1)

    prop = Property(
        name="event_date", type="datetime", before=limit_before, after=limit_after
    )
    type_def = TypeDef(name="Event", properties=[prop])

    models = gen_pydantic_models([type_def])
    Event = models["Event"]

    # Valid case
    valid_date = datetime.datetime(2024, 6, 15)
    e = Event(event_date=valid_date)
    assert getattr(e, "event_date") == valid_date

    # Invalid: too late
    with pytest.raises(ValidationError) as exc:
        Event(event_date=datetime.datetime(2025, 1, 2))
    assert f"Value must be before {limit_before}" in str(exc.value)

    # Invalid: too early
    with pytest.raises(ValidationError) as exc:
        Event(event_date=datetime.datetime(2022, 12, 31))
    assert f"Value must be after {limit_after}" in str(exc.value)


def test_path_validation(tmp_path):
    """Test filesystem path validation constraints."""

    # Create some dummy files
    f = tmp_path / "test.txt"
    f.touch()

    d = tmp_path / "subdir"
    d.mkdir()

    prop_exists = Property(name="p_exists", type="path", path_exists=True)
    prop_file = Property(name="p_file", type="path", is_file=True)
    prop_dir = Property(name="p_dir", type="path", is_dir=True)
    prop_ext = Property(name="p_ext", type="path", file_ext=[".txt", ".log"])

    type_def = TypeDef(
        name="FileCheck", properties=[prop_exists, prop_file, prop_dir, prop_ext]
    )

    models = gen_pydantic_models([type_def])
    FileCheck = models["FileCheck"]

    # Valid case
    fc = FileCheck(p_exists=str(f), p_file=str(f), p_dir=str(d), p_ext=str(f))
    assert getattr(fc, "p_exists") == str(f)

    # Invalid: path does not exist
    with pytest.raises(ValidationError) as exc:
        FileCheck(
            p_exists=str(tmp_path / "ghost"), p_file=str(f), p_dir=str(d), p_ext=str(f)
        )
    assert "does not exist" in str(exc.value)

    # Invalid: is_file but got dir
    with pytest.raises(ValidationError) as exc:
        FileCheck(p_exists=str(f), p_file=str(d), p_dir=str(d), p_ext=str(f))
    assert "is not a file" in str(exc.value)

    # Invalid: is_dir but got file
    with pytest.raises(ValidationError) as exc:
        FileCheck(p_exists=str(f), p_file=str(f), p_dir=str(f), p_ext=str(f))
    assert "is not a directory" in str(exc.value)

    # Invalid: bad extension
    bad_ext = tmp_path / "image.png"
    bad_ext.touch()
    with pytest.raises(ValidationError) as exc:
        FileCheck(p_exists=str(f), p_file=str(f), p_dir=str(d), p_ext=str(bad_ext))
    assert "File extension '.png' not allowed" in str(exc.value)


def test_url_validation():
    """Test URL validation constraints."""
    prop_proto = Property(name="u_proto", type="url", url_protocols=["https", "ftp"])
    prop_base = Property(name="u_base", type="url", url_base="https://api.example.com")

    type_def = TypeDef(name="WebResource", properties=[prop_proto, prop_base])

    models = gen_pydantic_models([type_def])
    WebResource = models["WebResource"]

    # Valid case
    wr = WebResource(
        u_proto="https://google.com", u_base="https://api.example.com/v1/users"
    )
    assert (
        str(getattr(wr, "u_proto")) == "https://google.com"
    )  # Pydantic v2 might not normalize 'str' type URLs automatically unless we use HttpUrl

    # Invalid: protocol
    with pytest.raises(ValidationError) as exc:
        WebResource(u_proto="http://insecure.com", u_base="https://api.example.com/v1")
    assert "Protocol 'http' not allowed" in str(exc.value)

    # Invalid: base
    with pytest.raises(ValidationError) as exc:
        WebResource(u_proto="https://google.com", u_base="https://other.com/api")
    assert "URL must start with 'https://api.example.com'" in str(exc.value)
