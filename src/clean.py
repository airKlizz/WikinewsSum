from gensim import utils

import json


class Clean:
    @classmethod
    def clean(cls, input_filename, json_bz_filename, output_filename):
        with utils.open(json_bz_filename, "rb") as f:
            articles = [json.loads(line) for line in f]
        t2t = {a["title"]: a["section_texts"][0] for a in articles}
        with open(output_filename, "w") as output_file:
            with open(input_filename) as input_file:
                for line in input_file:
                    entry = json.loads(line)
                    if entry["title"] in t2t.keys():
                        entry["text"] = t2t[entry["title"]]
                    output_file.write(json.dumps(entry))
                    output_file.write("\n")
