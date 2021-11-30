import json
import logging
import re
from os import listdir
from os.path import isfile, join
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import cElementTree

import pandas as pd
from gensim.corpora.wikicorpus import filter_wiki, get_namespace
from gensim.scripts.segment_wiki import extract_page_xmls
from smart_open import open
from tqdm import tqdm

logger = logging.getLogger(__name__)


class Wikinews:

    sources_translations = [
        "quellen",
        "sources",
        "quelle",
        "source",
        "fuentes",
        "fontes",
        "fonti",
        "źródła",
    ]

    category_pattern = re.compile(
        "\[\[(Category|Kategorie|Catégorie|Categorías|Categor\u00eda|Categorias|Categoria|Categorie|Kategorie|Kategoria):(.*?)\]\]"
    )
    footnote_pattern = re.compile(r"==(.+?)==(.+?)\n *\n", flags=re.DOTALL)
    url_pattern = re.compile(r"https?://[^\s|\]]+")
    blank_pattern = re.compile(r"^\s*$")
    to_remove_pattern = r"\[\[File:[^\]]+\]\]"
    to_remove_pattern_bis = r"{{[^w][^}]+}}"
    intern_link_pattern = r"{{w\|[^|}]+\|(?P<name>[^}]+)}}"
    intern_link_pattern_bis = r"{{w\|(?P<name>[^}]+)}}"
    promote_pattern = r"\[\[(?P<name>[^\]\|]+)\]\]"
    promote_pattern_bis = r"\[\[[^\]\|]+\|(?P<name>[^\]]+)\]\]"
    source_link_pattern = r"\[http[\S]* (?P<name>[^\]]+)\]"

    @classmethod
    def find_sources(cls, text):
        sources = []
        for footnote in cls.footnote_pattern.findall(text):
            footnote_title = list(footnote)[0].replace(" ", "").lower()
            footnote_content = list(footnote)[1].split("\n*")[1:]
            if footnote_title in cls.sources_translations:
                for raw_source in footnote_content:
                    sources += cls.url_pattern.findall(raw_source)
        return sources

    @classmethod
    def clean_sources(cls, sources):
        cleaned_sources = []
        for source in sources:
            parse = urlparse(source)
            if (parse.path == "" or parse.path == "/") and parse.params == "" and parse.query == "":
                continue
            cleaned_sources.append(source)
        return cleaned_sources

    @classmethod
    def clean_text(cls, text):
        text = re.sub(cls.to_remove_pattern, "", text)
        text = re.sub(cls.to_remove_pattern_bis, "", text)
        text = re.sub(cls.intern_link_pattern, r"\1", text)
        text = re.sub(cls.intern_link_pattern_bis, r"\1", text)
        text = re.sub(cls.promote_pattern, r"\1", text)
        text = re.sub(cls.promote_pattern_bis, r"\1", text)
        text = re.sub(cls.source_link_pattern, r"\1", text)
        return text

    @classmethod
    def get_pages_from_wiki_dump(cls, dump_path, max_doc_count):
        with open(dump_path, "rb") as xml_fileobj:
            page_xmls = extract_page_xmls(xml_fileobj)
            i = 0
            wrong_ns = 0
            no_sources = 0
            no_text = 0
            redirect = 0
            docs = []
            for i, page_xml in tqdm(enumerate(page_xmls)):
                elem = cElementTree.fromstring(page_xml)
                filter_namespaces = ("0",)
                namespace = get_namespace(elem.tag)
                ns_mapping = {"ns": namespace}
                text_path = "./{%(ns)s}revision/{%(ns)s}text" % ns_mapping
                title_path = "./{%(ns)s}title" % ns_mapping
                ns_path = "./{%(ns)s}ns" % ns_mapping
                title = elem.find(title_path).text
                text = elem.find(text_path).text
                ns = elem.find(ns_path).text
                if ns not in filter_namespaces:
                    wrong_ns += 1
                    continue
                try:
                    if (
                        title == "Une photojournaliste française « assassinée » en Centrafrique"
                        or title
                        == "Élection présidentielle française de 2012 : François Hollande dévoile ses 60 engagements"
                    ):
                        print(title)
                        print(text)
                        print()
                    categories = [c for _, c in cls.category_pattern.findall(text)]
                    sources = cls.find_sources(text)
                    cleaned_text = cls.category_pattern.sub("", text)
                    cleaned_text = cls.footnote_pattern.sub("", cleaned_text)
                    if (
                        title == "Une photojournaliste française « assassinée » en Centrafrique"
                        or title
                        == "Élection présidentielle française de 2012 : François Hollande dévoile ses 60 engagements"
                    ):
                        print(cleaned_text)
                        print()
                    cleaned_text = cls.clean_text(cleaned_text)
                    if (
                        title == "Une photojournaliste française « assassinée » en Centrafrique"
                        or title
                        == "Élection présidentielle française de 2012 : François Hollande dévoile ses 60 engagements"
                    ):
                        print(cleaned_text)
                        print()
                    passages = [
                        passage for passage in cleaned_text.split("\n\n") if cls.blank_pattern.match(passage) == None
                    ]
                    sources = cls.clean_sources(sources)
                    if len(" ".join(passages).split()) == 0:
                        no_text += 1
                        continue
                    if "#REDIRECT" in cleaned_text or "#redirect" in cleaned_text:
                        redirect += 1
                        continue
                    if sources == []:
                        no_sources += 1
                        continue
                    docs.append(
                        {
                            "title": title,
                            "text": passages,
                            "categories": categories,
                            "sources": sources,
                        }
                    )
                    if 0 < max_doc_count < len(docs):
                        break
                except (TypeError, ValueError) as e:
                    logger.error(f"Cannot read page #{i} - {title}: {e}")
        print(
            "Pages read: {}\nPages returned: {}\nWrong namespace: {}\nNo sources: {}\nNo text: {}\nRedirect: {}".format(
                i + 1, len(docs), wrong_ns, no_sources, no_text, redirect
            )
        )

        return docs

    @classmethod
    def save(cls, dump_path, max_doc_count=0, folder="wikinews"):
        docs = cls.get_pages_from_wiki_dump(dump_path=dump_path, max_doc_count=max_doc_count)
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "docs.json", "w") as f:
            json.dump({"docs": docs}, f, indent=2)
        sources = []
        for doc in docs:
            sources += doc["sources"]
        with open(path / "sources.txt", "w") as f:
            for source in sources:
                f.write(f"{source}\n")
