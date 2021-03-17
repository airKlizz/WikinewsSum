import json
from pathlib import Path

from newsplease import NewsPlease
from tqdm import tqdm


class Content:
    @classmethod
    def extract(cls, folder="sources"):
        pages_path = Path(folder) / "pages"
        contents_path = Path(folder) / "contents"
        contents_path.mkdir(parents=True, exist_ok=True)
        files = list(pages_path.glob("*"))
        for filename in tqdm(files, desc="Extract content from html"):
            try:
                with open(filename) as f:
                    html = f.read()
                article = NewsPlease.from_html(html, url=None)
                content = {
                    "title": article.title,
                    "maintext": article.maintext,
                    "language": article.language,
                }
                with open(contents_path / filename.name, "w") as f:
                    json.dump(content, f, sort_keys=True, indent=4)
            except Exception as e:
                print(e)
                pass
