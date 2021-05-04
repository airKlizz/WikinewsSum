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

## Step 6: Zip everything

```bash
zip -r enwikinewssum.zip endataset/ sources/ enwikinews/
```

## Step 6 bis: Create one big json file

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

## Step 7: Load it using datasets

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="endataset.json")
```