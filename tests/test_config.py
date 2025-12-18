import yaml

from staffsergeant import Config


def test_defaults():
    c = Config()
    d = c.as_dict()
    assert d["web_root"] == "docs"
    assert d["styles"] == "_styles"
    assert d["templates"] == "_templates"
    assert d["index_page"] == "index.html"
    assert d["post_source"] == "_posts"
    assert d["blog_title"] == "My Blog"


def test_from_file(tmp_path):
    data = {
        "web_root": "out",
        "styles": "css",
        "templates": "tpl",
        "index_page": "home.html",
        "post_source": "posts_src",
        "post_output": "out/posts",
        "blog_title": "Test Blog",
    }
    p = tmp_path / "test_ssg.yaml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")

    c = Config.from_file(str(p))
    d = c.as_dict()
    assert d["web_root"] == "out"
    assert d["styles"] == "css"
    assert d["templates"] == "tpl"
    assert d["index_page"] == "home.html"
    assert d["post_source"] == "posts_src"
    assert d["post_output"] == "out/posts"
    assert d["blog_title"] == "Test Blog"
