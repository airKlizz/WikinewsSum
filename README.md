# Creation WikinewsSum

```bash
cd wikinewssum
```

## Step 1: Wikinews Dump

First you need to download the Wikinews dump you want to create the dataset from.

> Replace with the language you want

```bash
cd dumps
wget https://dumps.wikimedia.org/enwikinews/latest/enwikinews-latest-pages-meta-current.xml.bz2
cd ..
```

## Step 2: Extract docs from dump

```python
from src import Wikinews
Wikinews.save(dump_path="dumps/enwikinews-latest-pages-meta-current.xml.bz2", max_doc_count=0, folder="enwikinews")
```

This will create 2 files in the `enwikinews` folder: `docs.json` that information of the Wikinews articles, and `sources.txt` that contains all the sources (1 per line).

## Step 3: Get sources

```python
from src import Sources
Sources.save(file="enwikinews/sources.txt", folder="sources", max_workers=5, timeout=10, retry=False)
```

> Can takes hours. You can stop it when you want and run it again, it will reuse the sources already saved if the folder parameter is the same. The sources didn't find will be skipped unless the retry parameter is set to True.

## Step 4: Extract content from sources

```python
from src import Content
Content.extract(folder="sources")
```

## Step 5: Create the dataset

```python
from src import Dataset
Dataset.create(wikinews_folder="enwikinews", sources_folder="sources", dataset_folder="endataset")
```

## (optional) Zip everything

```bash
zip -r enwikinewssum.zip endataset/ sources/ enwikinews/
```

## Step 6: Create one big json file

```python
import json
from pathlib import Path

dataset_folder = Path("endataset")
files = list(dataset_folder.glob("**/*.json"))
with open("endataset.json", "w") as output_file:
    for filename in files:
        with open(filename) as f:
            entry = json.load(f)
        output_file.write(json.dumps(entry))
        output_file.write("\n")
```

## Step 7: Clean the texts by using another text extraction method (which removed the sources, this is why it was not used in the first place)

```bash
python -m gensim.scripts.segment_wiki -i -f dumps/enwikinews-latest-pages-meta-current.xml.bz2 -o dumps/enwikinews-latest.json.gz
```

```python
from utils import Clean
Clean.clean("endataset.json", "dumps/enwikinews-latest.json.gz", "cleaned_endataset.json")
```

## Step 8: Create the final json file

```python
import json
from pathlib import Path

json_filenames = {
    "de": "datasets/dedataset_with_urls.json",
    "en": "datasets/endataset_with_urls.json",
    "es": "datasets/esdataset_with_urls.json",
    "fr": "datasets/frdataset_with_urls.json",
    "it": "datasets/itdataset_with_urls.json",
    "pl": "datasets/pldataset_with_urls.json",
    "pt": "datasets/ptdataset_with_urls.json",
}

final_json_filename = "wikinewssum.json"

with open(final_json_filename, "w") as final_json:
    for language, json_filename in json_filenames.items():
        with open(json_filename) as json_file:
            data = json_file.read()
        for entry_str in data.split("\n"):
            if entry_str is None or entry_str == "":
                continue
            entry = json.loads(entry_str)
            new_entry = {
                "language": language,
                "title": entry["title"],
                "news": entry["text"],
                "categories": entry["categories"],
                "sources": []
            }
            for source in entry["sources"]:
                new_entry["sources"].append({
                    "language": source["language"],
                    "title": source["title"],
                    "text": source["maintext"],
                    "url": source["url"],
                    "archive_url": source["archive_url"]
                })
            final_json.write(json.dumps(new_entry))
            final_json.write("\n")



```

## Step 8: Filter samples

```python
from src import Filter
Filter.filter("wikinewssum.json", "filtered_wikinewssum.json")
```

## Step 7: Load it using datasets

```python
from datasets import load_dataset
dataset = load_dataset("json", data_files="filtered_wikinewssum.json")
```
