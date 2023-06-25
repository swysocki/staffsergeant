# SSG or Staff SerGeant (a Static Site Generator)

A Python-based static site generator that is compatible with Jekyll content.
The main focus of SSG is for my blog, but it is easy enough to extend for
other purposes.  SSG is quite minimal, it provides a base set of templates
for creating an index page and blog posts. Styling and additional pages are
left up to the user.

## Quickstart

1. Clone this project
2. Create a Python Virtual Environment and install the dependencies
3. Copy your blog posts to the `_posts` directory
4. Run `python3 ssg.py` from the root of the project
5. (Optional) View your website locally by running `python3 ssg.py render`