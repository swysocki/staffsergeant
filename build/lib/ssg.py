"""Minimal Python SSG

Does just enough to generate a static website
- Generate HTML from a folder of Markdown files
- Insert the files into a template so they can be found
"""

import glob
import os
import pathlib
import re
import shutil
import sys

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
            page = BlogPost(page)
            if not page.front_matter:
                continue
            title = page.front_matter.get("title")
            href = os.path.join("posts", str(page.html_filename))
            index_list.append(
                {"post_title": title, "post_link": href, "date": page.post_date}
            )

        env = Environment(loader=FileSystemLoader(self.templates))
        template = env.get_template(index_template)
        content = template.render(page_title=self.blog_title, post_list=index_list)
        index_path = os.path.join(self.web_root, self.index_page)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_posts(self):
        post_template = "post.html.j2"
        for page in self.post_list:
            pg = BlogPost(page)
            post_out_path = os.path.join(self.post_output, pg.html_filename)
            if not pg.front_matter:
                continue
            post_title = pg.front_matter.get("title")
            page_title = f"{self.blog_title}::{post_title}"
            env = Environment(loader=FileSystemLoader(self.templates))
            template = env.get_template(post_template)
            content = template.render(
                post_title=post_title,
                body_content=pg.html,
                page_title=page_title,
                post_date=pg.post_date,
            )
            with open(post_out_path, "w", encoding="utf-8") as file:
                file.write(content)

    def _create_styles(self):
        """Process CSS files if they exist"""
        styles_dir = os.path.join(self.web_root, "styles")
        css_files = glob.glob(os.path.join(self.styles, "*.css"))
        if css_files:
            if not os.path.exists(styles_dir):
                os.mkdir(styles_dir)
            for file in css_files:
                shutil.copy(file, styles_dir)

    def generate(self):
        """Call all methods that create the website"""
        self._create_index()
        self._create_posts()
        self._create_styles()


class BlogPost:
    """BlogPost class represent a single markdown post and its attributes"""

    post_extension = ".html"

    def __init__(self, markdown_post: str):
        self.md_path = pathlib.Path(markdown_post)
        self.html_filename = pathlib.Path(self.md_path.stem).with_suffix(
            self.post_extension
        )
        self.post_text = self.md_path.read_text(encoding="utf-8")
        self._md = (
            MarkdownIt("commonmark", {"breaks": False, "html": True})
            .use(front_matter_plugin)
            .enable("table")
        )

    @property
    def post_date(self) -> str:
        date_re = r"(\d{4}-\d{2}-\d{2})"
        result = re.match(date_re, self.md_path.stem)
        if result:
            return result.group()
        return ""

    @property
    def front_matter(self) -> dict | None:
        """Frontmatter of post in YAML format

        YAML frontmatter is mandatory as we set the title and other
        attributes from there
        """
        tokens = self._md.parse(self.post_text)
        for token in tokens:
            if token.type == "front_matter":
                fm = yaml.safe_load(token.content)
                return fm
            else:
                print(f"Error: missing frontmatter for post: {self.html_filename}")
                return None

    @property
    def html(self):
        """HTML body of a BlogPost"""
        return self._md.render(self.post_text)


app = typer.Typer()

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
