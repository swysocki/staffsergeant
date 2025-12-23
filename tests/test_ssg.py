from ssg import BlogPost, SSGBlog
import os


def test_blog_post_date(tmp_path):
    """Given a filepath with a date, the post_date property should
    return the date in the correct format
    """
    # Arrange
    p = tmp_path / "2025-11-01-test-post.md"
    p.write_text("---\ntitle: Test Post\n---\n\nHello, world.")
    post = BlogPost(p)

    # Act
    actual_date = post.post_date

    # Assert
    assert actual_date == "2025-11-01"


def test_blog_post_front_matter(tmp_path):
    """Given a markdown file with frontmatter, the front_matter property should
    return a dictionary with the frontmatter content.
    """
    # Arrange
    p = tmp_path / "test-post.md"
    p.write_text("---\ntitle: My Test Title\nauthor: John Doe\n---\n\nPost content.")
    post = BlogPost(p)

    # Act
    front_matter = post.front_matter

    # Assert
    assert front_matter == {"title": "My Test Title", "author": "John Doe"}


def test_blog_post_html(tmp_path):
    """Given a markdown file, the html property should return the rendered HTML."""
    # Arrange
    p = tmp_path / "test-post.md"
    p.write_text("---\ntitle: Test\n---\n\n# A Heading\n\nSome text.")
    post = BlogPost(p)

    # Act
    html = post.html

    # Assert
    assert "<h1>A Heading</h1>" in html
    assert "<p>Some text.</p>" in html


def test_generate_creates_site(tmp_path, monkeypatch):
    # Arrange - create minimal templates and a post
    src = tmp_path
    posts = src / "_posts"
    templates = src / "_templates"
    static = src / "_static"
    posts.mkdir()
    templates.mkdir()
    static.mkdir()

    # write a simple post
    post_file = posts / "2025-12-20-sample.md"
    post_file.write_text("---\ntitle: Sample Post\n---\n\n# Hello\n\nBody")

    # write templates
    (templates / "base.html.j2").write_text(
        "<html><head><title>{{ page_title }}</title></head><body>{% block content %}{% endblock %}</body></html>"
    )
    (templates / "index.html.j2").write_text(
        "{% extends 'base.html.j2' %}{% block content %}<ul>{% for post in post_list %}<li><a href='{{ post.post_link }}'>{{ post.post_title }}</a></li>{% endfor %}</ul>{% endblock %}"
    )
    (templates / "post.html.j2").write_text(
        "{% extends 'base.html.j2' %}{% block content %}<article><h2>{{ post_title }}</h2>{{ body_content }}</article>{% endblock %}"
    )

    # add a static file
    (static / "robots.txt").write_text("User-agent: *")

    # monkeypatch current working directory to tmp source
    monkeypatch.chdir(src)

    # Act
    blog = SSGBlog(str(src))
    blog.templates = str(templates)
    blog.generate()

    # Assert - index created
    index_path = os.path.join(SSGBlog.web_root, SSGBlog.index_page)
    assert os.path.exists(index_path)
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Sample Post" in content

    # Assert - post created
    post_out = os.path.join(SSGBlog.post_output, "2025-12-20-sample.html")
    assert os.path.exists(post_out)
    with open(post_out, "r", encoding="utf-8") as f:
        pcont = f.read()
    assert "Hello" in pcont

    # Assert - static copied
    static_out = os.path.join(SSGBlog.web_root, "static", "robots.txt")
    assert os.path.exists(static_out)


def test_copy_static_files_copies(tmp_path, monkeypatch):
    src = tmp_path
    static = src / "_static"
    static.mkdir()
    (static / "file.txt").write_text("content")

    # monkeypatch cwd to src
    monkeypatch.chdir(src)

    blog = SSGBlog(str(src))
    blog.copy_static_files()

    dest = os.path.join(SSGBlog.web_root, "static", "file.txt")
    assert os.path.exists(dest)
    with open(dest, "r", encoding="utf-8") as f:
        assert f.read() == "content"


def test_copy_static_files_no_static(tmp_path, monkeypatch):
    src = tmp_path
    # no _static created
    monkeypatch.chdir(src)

    blog = SSGBlog(str(src))
    # should not raise
    blog.copy_static_files()

    # docs/static should not exist
    assert not os.path.exists(os.path.join(SSGBlog.web_root, "static"))
