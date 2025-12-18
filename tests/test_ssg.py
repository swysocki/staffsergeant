from staffsergeant import BlogPost


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
