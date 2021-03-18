import json
from pathlib import Path

from newsplease import NewsPlease
from tqdm import tqdm
import concurrent.futures as cf



class Content:
    
    @classmethod
    def save(cls, filename, contents_path):
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
    
    @classmethod
    def extract(cls, folder="sources", max_workers=10):
        pages_path = Path(folder) / "pages"
        contents_path = Path(folder) / "contents"
        contents_path.mkdir(parents=True, exist_ok=True)
        files = list(pages_path.glob("*"))
        with cf.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for filename in tqdm(files, desc="Extract content from html"):
                futures.append(
                    executor.submit(
                        cls.save,
                        filename=filename,
                        contents_path=contents_path,
                    )
                )
            for future in cf.as_completed(futures):
                future.result()
