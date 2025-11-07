import asyncio
from ssg import BlogPost, SSGBlog


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


def test_ssg_blog_generate_multiple_posts(tmp_path):
    """
    Given a source directory with multiple markdown files, the generate method
    should create the corresponding HTML files.
    """
    # Arrange
    source_path = tmp_path
    (source_path / "_posts").mkdir()
    (source_path / "_posts" / "2025-11-01-post-one.md").write_text(
        "---\ntitle: Post One\n---\n\n# Post One\n\nContent for post one."
    )
    (source_path / "_posts" / "2025-11-02-post-two.md").write_text(
        "---\ntitle: Post Two\n---\n\n# Post Two\n\nContent for post two."
    )
    (source_path / "_templates").mkdir()
    (source_path / "_templates" / "base.html.j2").write_text("{{ content }}")
    (source_path / "_templates" / "index.html.j2").write_text(
        # ruff: noqa: E501
        '{% for post in post_list %}<a href="{{ post.post_link }}">{{ post.post_title }}</a>{% endfor %}'
    )
    (source_path / "_templates" / "post.html.j2").write_text(
        "<h1>{{ post_title }}</h1><div>{{ body_content }}</div>"
    )

    # Act
    blog = SSGBlog(str(source_path))

    asyncio.run(blog.generate())

    # Assert
    output_path = source_path / blog.web_root
    post_one_html = output_path / "posts" / "2025-11-01-post-one.html"
    post_two_html = output_path / "posts" / "2025-11-02-post-two.html"
    index_html = output_path / "index.html"

    assert post_one_html.exists()
    assert post_two_html.exists()
    assert index_html.exists()

    post_one_content = post_one_html.read_text()
    assert "<h1>Post One</h1>" in post_one_content
    assert "<h1>Post One</h1>" in post_one_content
    assert "<p>Content for post one.</p>" in post_one_content

    post_two_content = post_two_html.read_text()
    assert "<h1>Post Two</h1>" in post_two_content
    assert "<h1>Post Two</h1>" in post_two_content
    assert "<p>Content for post two.</p>" in post_two_content

    index_content = index_html.read_text()
    assert '<a href="posts/2025-11-02-post-two.html">Post Two</a>' in index_content
    assert '<a href="posts/2025-11-01-post-one.html">Post One</a>' in index_content
