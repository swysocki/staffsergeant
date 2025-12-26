"""Minimal Python SSG

Does just enough to generate a static website
- Generate HTML from a folder of Markdown files
- Insert the files into a template so they can be found
"""

from dataclasses import dataclass
from typing import Optional
import glob
import os
import pathlib
import shutil

import typer

from jinja2 import Environment, FileSystemLoader
import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter.index import front_matter_plugin


class SSGBlog:
    """GenerateBlog class contains the ingredients to transform the Markdown pages
    into an HTML website. The class takes `inputs` and creates a website as an
    `output`.  The following structure defines the input and output conventions.  These
    conventions allow me to use the previous Jekyll structure without reformatting
    my posts.
    """

    # TODO: make this a config file
    web_root = "docs"  # if using Github pages
    styles = "_styles"
    templates = "_templates"
    index_page = "index.html"
    post_source = "_posts"
    post_output = os.path.join(web_root, "posts")
    blog_title = "My Blog"

    def __init__(self, source_path: str):
        self.source_path = source_path
        pathlib.Path(self.web_root).mkdir(exist_ok=True)
        pathlib.Path(self.post_output).mkdir(exist_ok=True)

    @property
    def post_list(self):
        """List of Markdown posts"""
        posts_path = os.path.join(self.source_path, self.post_source)
        posts = list(glob.glob(os.path.join(posts_path, "*.md")))
        posts.sort(reverse=True)
        return posts

    def _create_index(self):
        index_template = "index.html.j2"
        index_list = []
        for page in self.post_list:
            # Prefer strict BlogPost parsing
            try:
                pg = BlogPost.from_markdown(page)
            except InvalidBlogPostError as err:
                print(f"Skipping post {page}: {err}")
                continue

            # only add posts with layout: post to the index
            if "post" not in (pg.layout or ""):
                continue
            title = pg.title
            href = os.path.join("posts", f"{pg.slug}.html")
            index_list.append({"post_title": title, "post_link": href, "date": pg.date})

        env = Environment(loader=FileSystemLoader(self.templates))
        template = env.get_template(index_template)
        content = template.render(page_title=self.blog_title, post_list=index_list)
        index_path = os.path.join(self.web_root, self.index_page)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_posts(self):
        post_template = "post.html.j2"
        for page in self.post_list:
            try:
                pg = BlogPost.from_markdown(page)
            except InvalidBlogPostError as err:
                print(f"Skipping post {page}: {err}")
                continue

            # only create HTML for posts with layout 'post'
            if "post" not in (pg.layout or ""):
                continue
            post_title = pg.title
            page_title = f"{self.blog_title}::{post_title}"
            env = Environment(loader=FileSystemLoader(self.templates))
            template = env.get_template(post_template)
            content = template.render(
                post_title=post_title,
                body_content=pg.content,
                page_title=page_title,
                post_date=pg.date,
            )
            post_out_path = os.path.join(self.post_output, f"{pg.slug}.html")
            with open(post_out_path, "w", encoding="utf-8") as file:
                file.write(content)

    def copy_static_files(self):
        """Copy static files to the web root"""
        static_dir = os.path.join(self.source_path, "_static")
        if os.path.exists(static_dir):
            dest_dir = os.path.join(self.web_root, "static")
            shutil.copytree(static_dir, dest_dir, dirs_exist_ok=True)

    def create_project_page(self):
        project_template = "project.html.j2"
        # this doesn't need to iterate over all posts, only those with layout: project
        # TODO: optimize this
        # this doesn't actaully need to exist. It can be treated like a regular page
        # and run from the _create_posts method above.
        # TODO: test removal of this method
        for post in self.post_list:
            try:
                pg = BlogPost.from_markdown(post)
            except InvalidBlogPostError as err:
                print(f"Skipping post {post}: {err}")
                continue

            post_out_path = os.path.join(self.web_root, f"{pg.slug}.html")
            if "project" in (pg.layout or ""):
                env = Environment(loader=FileSystemLoader(self.templates))
                template = env.get_template(project_template)
                content = template.render(
                    post_title=pg.title,
                    body_content=pg.content,
                    page_title=f"{self.blog_title}::{pg.title}",
                )
                with open(post_out_path, "w", encoding="utf-8") as file:
                    file.write(content)

    def generate(self):
        """Call all methods that create the website"""
        self._create_index()
        self._create_posts()
        self.create_project_page()
        self.copy_static_files()


@dataclass
class BlogPost:
    """BlogPost class represent a single markdown post and its attributes"""

    title: str
    date: str
    layout: str
    slug: str
    content: str = ""
    excerpt: Optional[str] = None
    source_path: str = ""

    @classmethod
    def from_markdown(cls, filepath: str) -> "BlogPost":
        md_path = pathlib.Path(filepath)
        post_text = md_path.read_text(encoding="utf-8")
        md = (
            MarkdownIt("commonmark", {"breaks": False, "html": True})
            .use(front_matter_plugin)
            .enable("table")
        )
        tokens = md.parse(post_text)
        front_matter = {}
        for token in tokens:
            if token.type == "front_matter":
                front_matter = yaml.safe_load(token.content) or {}
                break
        content = md.render(post_text)

        if not front_matter:
            raise InvalidBlogPostError(f"Missing front matter in {filepath}")

        missing = [
            k for k in ("title", "date", "layout", "slug") if not front_matter.get(k)
        ]
        if missing:
            raise InvalidBlogPostError(
                f"Missing mandatory front matter fields {missing} in {filepath}"
            )

        return cls(
            title=str(front_matter.get("title")),
            date=str(front_matter.get("date")),
            layout=str(front_matter.get("layout")),
            slug=str(front_matter.get("slug")),
            content=content,
            source_path=filepath,
        )


class InvalidBlogPostError(Exception):
    """Raised when a markdown post is missing required front matter."""

    pass


app = typer.Typer()


@app.command()
def initialize():
    """
    Initializes a new project directory.
    """
    print("Initialize command is not yet implemented.")


@app.command()
def clean():
    """
    Clean the generated site.
    """
    if os.path.exists(SSGBlog.web_root):
        shutil.rmtree(SSGBlog.web_root)
        print(f"Removed directory: {SSGBlog.web_root}")
    else:
        print(f"No generated site found at: {SSGBlog.web_root}")


@app.command()
def generate():
    """
    Generate the static site.
    """
    blog = SSGBlog(".")
    blog.generate()
    print("Site generated successfully.")


def main():
    app()


if __name__ == "__main__":
    main()
