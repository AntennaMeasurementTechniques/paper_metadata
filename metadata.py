from collections import defaultdict
from datetime import *
import csv
import os
import re
import subprocess
from lxml import etree

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

I4A_PATH = '/files/amta_paper_archive/2018/'  # For doc_location column
OUTPUT_FILENAME = 'i4a_paper_upload.csv'

DOC_DATE = '11/04/2018'
DATE_ADDED = date.today().strftime("%m/%d/%Y")

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
GROBID_DIR = os.path.join(THIS_DIR, "grobid")
PDF_DIR = os.path.join(THIS_DIR, "2018")

KEYWORD_FILE = os.path.join(THIS_DIR, "keywords.txt")

CAT_IDS = {
    (24, 'Absorber'),
    (26, 'Accuracy'),
    (28, 'Alignment'),
    (27, 'Analysis'),
    (25, 'Anechoic Chamber'),
    (29, 'Calibration'),
    (30, 'Compact Range'),
    (31, 'Errors'),
    (32, 'Far Field'),
    (32, 'Far-Field'),
    (33, 'Ground Bounce'),
    (34, 'Ground Plane'),
    (35, 'Holography'),
    (36, 'History'),
    (37, 'Imaging'),
    (38, 'Impedance'),
    (39, 'Instrumentation'),
    (40, 'Intermodulation'),
    (41, 'Materials'),
    (42, 'Near Field'),
    (42, 'Near-Field'),
    (43, 'Pattern'),
    (44, 'Phased Array'),
    (45, 'Polarization'),
    (46, 'Radar'),
    (47, 'RCS'),
    (48, 'Certification'),
    (49, 'Scale Model'),
    (50, 'Tapered Chamber'),
    (51, 'Time Domain'),
}

DEFAULT_CAT_ID = 52

CATEGORY_TO_ID = {v.lower(): k for k, v in CAT_IDS}


def get_pdf_filenames(dirname):
    return [fn for fn in os.listdir(dirname) if fn.endswith('.pdf')]


def generate_intermediate_files(pdf_filenames):
    # Text files for keyword search
    for fn in pdf_filenames:
        subprocess.run(["pdftotext", os.path.join(PDF_DIR, fn)])

    # XML files for metadata extraction
    subprocess.run([
        "java",
        "-Xmx1G",
        "-jar",
        os.path.join(GROBID_DIR, "grobid-core", "build", "libs", "grobid-core-0.5.2-onejar.jar"),
        "-gH",
        os.path.join(GROBID_DIR, "grobid-home"),
        "-dIn",
        PDF_DIR,
        "-dOut",
        PDF_DIR,
        "-exe",
        "processHeader"])


def extract_metadata(filename):
    tree = etree.parse(open(filename))


    # Title
    title = tree.find(".//tei:title", NS).text

    # Authors
    authors = []
    for author_el in tree.iterfind(".//tei:author", NS):
        fn = ""
        mn = ""
        sn = ""
        for forename_el in author_el.iterfind(".//tei:forename", NS):
            if "type" in forename_el.attrib:
                if forename_el.attrib["type"] == "first":
                    fn = forename_el.text

                if forename_el.attrib["type"] == "middle":
                    mn = forename_el.text

        for surname in author_el.iterfind(".//tei:surname", NS):
            sn = surname.text

        authors.append(" ".join(filter(lambda n: n, [fn, mn, sn])))


    # Abstract
    abstract_el = tree.find(".//tei:abstract", NS)
    if abstract_el.text.strip() != '':
        abstract = abstract_el.text
    else:
        abstract = " ".join(map(lambda c: c.text, abstract_el.getchildren()))

    return({"title": title,
            "authors": ", ".join(authors),
            "abstract": abstract})


def parse_keywords_file():
    def tree():
        return defaultdict(tree)

    def untree(d):
        if isinstance(d, defaultdict):
            for k, v in d.items():
                d[k] = untree(v)
            return dict(d)
        else:
            return d

    keywords_tree = defaultdict(tree)
    key_phrases = set([])

    with open(KEYWORD_FILE) as f:
        for key_phrase in f.readlines():
            key_phrase = key_phrase.strip()
            key_phrases.add(key_phrase)
            subkw = keywords_tree
            for w in key_phrase.split(' '):
                subkw = subkw[w]

    return [untree(keywords_tree), key_phrases]


def get_keywords(pdf_filename, keywords_tree, key_phrases):
    paper_keywords = set([])
    # Assume txt already generated
    with open(pdf_filename.replace("pdf", "txt")) as f:
        words = list(filter(lambda s: s != "",
                            map(lambda s: s.strip(),
                                re.split("\W+", f.read().lower()))))

        for i, word in enumerate(words):
            j = 1
            next_word = word
            subtree = keywords_tree
            while i + j < len(words):
                if next_word in subtree:
                    paper_keywords.add(" ".join(words[i: i + j]))
                    subtree = subtree[next_word]
                    next_word = words[i + j]
                    j = j + 1
                else:
                    break

    return paper_keywords.intersection(key_phrases)


def get_category_ids(pdf_filename):
    with open(pdf_filename.replace("pdf", "txt")) as f:
        words = list(filter(lambda s: s != "",
                            map(lambda s: s.strip(),
                                re.split("\W+", f.read().lower()))))

        categories = set([])

        for word in words:
            if word in CATEGORY_TO_ID:
                categories.add(CATEGORY_TO_ID[word])

    if len(categories) == 0:
        categories.add(DEFAULT_CAT_ID)

    return categories



def build_i4a_upload(metadata_dict, keywords_tree, key_phrases):
    '''
        metadata_dict should look like:
        {
            filename: {authors: [], title: "", abstract: ""}
        }
    '''
    header = ["doc_category_ids",
              "doc_location",
              "doc_title",
              "doc_author",
              "doc_description",
              "doc_keywords",
              "bMembersOnly",
              "doc_date",
              "date_added",
              "bFeatured"]

    with open(os.path.join(PDF_DIR, "i4a_paper_upload.csv"), "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for fn, metadata in metadata_dict.items():
            floc = os.path.join(PDF_DIR, fn)
            line = [", ".join(map(str, get_category_ids(floc))),
                    I4A_PATH + fn,
                    metadata["title"],
                    metadata["authors"],
                    metadata["abstract"],
                    ", ".join(get_keywords(floc, keywords_tree, key_phrases)),
                    "yes",
                    DOC_DATE,
                    DATE_ADDED,
                    "no"]
            writer.writerow(line)


def build_metadata_dict(pdf_filenames):

    metadata_dict = {}

    for fn in pdf_filenames:
        metadata_dict[fn] = extract_metadata(os.path.join(PDF_DIR, fn.replace("pdf", "tei.xml")))

    return metadata_dict


if __name__ == "__main__":
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pdf_filenames = get_pdf_filenames(PDF_DIR)
    keywords_tree, key_phrases = parse_keywords_file()
    # print("Keywords:\n", get_keywords(os.path.join(PDF_DIR, 'A18-0006.pdf'), keywords_tree, key_phrases))
    # print("\nCategory IDs:\n", get_category_ids(os.path.join(PDF_DIR, 'A18-0006.pdf')))
    # print(pdf_filenames)
    # generate_intermediate_files(pdf_filenames)
    metadata_dict = build_metadata_dict(pdf_filenames)
    build_i4a_upload(metadata_dict, keywords_tree, key_phrases)
    # pp.pprint(metadata_dict)
    # print(extract_metadata(os.path.join(PDF_DIR, 'A18-0006.pdf.tei.xml')))
