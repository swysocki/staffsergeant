import os
from dataclasses import asdict, dataclass
from typing import Any, Dict

import yaml


@dataclass
class Config:
    """Typed configuration for the SSG.

    Values are read from `ssg.yaml` when using `Config.from_file()`.
    Using a dataclass gives proper attributes and typing for consumers.
    """

    web_root: str = "docs"
    styles: str = "_styles"
    templates: str = "_templates"
    index_page: str = "index.html"
    post_source: str = "_posts"
    post_output: str = ""
    blog_title: str = "My Blog"

    def __post_init__(self) -> None:
        if not self.post_output:
            self.post_output = os.path.join(self.web_root, "posts")

    @classmethod
    def from_file(cls, path: str = "ssg.yaml") -> "Config":
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            # Only pass known dataclass fields to the constructor
            valid: Dict[str, Any] = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        return cls()

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)
