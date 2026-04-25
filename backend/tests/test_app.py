from app import create_app
from app.extensions import db
from app.services.identity import build_mpid, hash_national_id, normalize_national_id


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "test"
    NATIONAL_ID_KEY = "0123456789abcdef0123456789abcdef"
    UPLOAD_DIR = "/tmp/test_uploads"


def test_health_endpoint():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_readiness_endpoint():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    client = app.test_client()
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["database"] == "up"


def test_national_id_normalization_and_hash_stability():
    raw = "123-45-6789"
    normalized = normalize_national_id(raw)
    assert normalized == "123456789"
    assert hash_national_id(raw) == hash_national_id(normalized)


def test_mpid_generation_format():
    national_id_hash = hash_national_id("123456789")
    mpid = build_mpid(national_id_hash)
    assert mpid.startswith("MPID-")
    assert len(mpid) == 25
