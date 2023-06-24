"""Minimal Python SSG

Does just enough to generate a static website
- Generate HTML from a folder of Markdown files
- Insert the files into a template so they can be found
"""
from genericpath import isdir
import glob
import os
import pathlib
import shutil

from jinja2 import Environment, FileSystemLoader
import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter.index import front_matter_plugin

INDEX_PAGE = "index.html"


class GenerateBlog:
    """ GenerateBlog class contains the ingredients to transform the Markdown pages
    into an HTML website. The class takes `inputs` and creates a website as an
    `output`.  The following structure defines the input and output conventions.  These
    conventions allow me to use the previous Jekyll structure without reformatting
    my posts.

    Inputs:
        _posts: markdown post directory
        templates: Jinja templates directory
        assets: 

    Outputs:
        web_root: a folder name "public" within the root of project
    """

    web_root = "public"
    index_page = "index.html"
    post_source = "_posts"
    post_output = os.path.join(web_root, "posts")

    def __init__(self, source_path: str):
        self.source_path = source_path
        pathlib.Path(self.web_root).mkdir(exist_ok=True)
        pathlib.Path(self.post_output).mkdir(exist_ok=True)

    @property
    def post_list(self):
        posts_path = os.path.join(self.source_path, self.post_source)
        posts = [file for file in glob.glob(os.path.join(posts_path, "*.md"))]
        posts.sort(reverse=True)
        return posts

    def _create_index(self):
        index_list = []
        for page in self.post_list:
            pg = BlogPost(page)
            title = pg.front_matter.get("title")
            href = os.path.join("posts", str(pg.html_filename))
            d = {"post_title": title, "post_link": href}
            index_list.append(d)

        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template("index.html.j2")
        content = template.render(post_list=index_list)
        index_path = os.path.join(self.web_root, self.index_page)
        with open(index_path, "w") as f:
            f.write(content)

    def _create_posts(self):
        for page in self.post_list:
            pg = BlogPost(page)
            post_out_path = os.path.join(self.post_output, pg.html_filename)
            with open(post_out_path, "w") as f:
                f.write(pg.html)

    def _create_assets(self):
        if os.path.isdir("assets"):
            shutil.copy("assets", os.path.join(self.web_root, "assets"))

    def generate(self):
        self._create_index()
        self._create_posts()
        self._create_assets() 

class BlogPost:
    post_extension = ".html"

    def __init__(self, markdown_post: str):
        self.md_path = pathlib.Path(markdown_post)
        self.html_filename = pathlib.Path(self.md_path.stem).with_suffix(self.post_extension)
        self.post_text = self.md_path.read_text()
        self._md = (
            MarkdownIt("commonmark", {"breaks": True, "html": True})
            .use(front_matter_plugin)
            .enable("table")
        )

    @property
    def front_matter(self):
        tokens = self._md.parse(self.post_text)
        for token in tokens:
            if token.type == "front_matter":
                fm = yaml.safe_load(token.content)
                return fm

    @property
    def html(self):
        return self._md.render(self.post_text)


if __name__ == "__main__":
    blog = GenerateBlog(".")
    blog.generate()