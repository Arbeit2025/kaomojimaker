import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app  # noqa: E402


def test_index_ok():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "かおもじメーカー" in html


def test_healthz():
    client = app.test_client()
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_data(as_text=True) == "ok"


def test_index_script_not_escaped():
    # |safe が無いと JS/CSS の引用符が HTML エスケープされてスクリプトが死ぬ回帰テスト
    client = app.test_client()
    html = client.get("/").get_data(as_text=True)
    assert "getElementById" in html
    assert "&#34;" not in html
    assert "&#39;" not in html


def test_index_has_categories_and_actions():
    client = app.test_client()
    html = client.get("/").get_data(as_text=True)
    for word in ["輪郭", "目", "口", "頬・照れ", "腕・手", "装飾",
                 "ランダム", "コピー", "お気に入りに保存", "プリセット"]:
        assert word in html
