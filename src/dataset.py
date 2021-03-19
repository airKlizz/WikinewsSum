import base64
import json
from pathlib import Path

from tqdm import tqdm


class Dataset:
    @classmethod
    def get_source(cls, url, sources_folder):
        urls_path = Path(sources_folder) / "urls"
        contents_path = Path(sources_folder) / "contents"
        url_path = urls_path / base64.b64encode(url.encode(), b"qw").decode("utf-8")[:254]
        with open(url_path) as f:
            archive_url = f.read()
        content_path = contents_path / base64.b64encode(archive_url.encode(), b"qw").decode("utf-8")[:254]
        with open(content_path) as f:
            source = json.load(f)
        return source

    @classmethod
    def create(cls, wikinews_folder="wikinews", sources_folder="sources", dataset_folder="dataset"):
        path = Path(dataset_folder)
        path.mkdir(parents=True, exist_ok=True)
        number_of_sources_lost = 0
        with open(Path(wikinews_folder) / "docs.json") as f:
            docs = json.load(f)
        for doc in tqdm(docs["docs"]):
            sources = []
            for url in doc["sources"]:
                try:
                    source = cls.get_source(url, sources_folder)
                    assert source["maintext"] is not None
                    sources.append(source)
                except:
                    number_of_sources_lost += 1
                    continue
            doc_with_sources = doc.copy()
            doc_with_sources["sources"] = sources
            with open(path / (doc_with_sources["title"].replace(" ", "_").replace("/", "_").lower() + ".json"), "w") as f:
                json.dump(doc_with_sources, f, indent=2)

        print(f"Number of sources lost {number_of_sources_lost}")
