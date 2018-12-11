This tool is for extracting metadata from research papers.  It extracts the following data:

- Title
- Authors
- Abstract
- Keywords and phrases
    - The master list of keywords can be found in `keywords.txt`
- i4a category ids

This metadata is then written to a .csv file formatted in the manner required by i4a.

This tool is developed for linux. Most likely it could be modified for Windows, but at the moment that is not officially supported.

## Dependencies

- [Grobid](https://grobid.readthedocs.io/en/latest/Install-Grobid/)
    - Should be installed in grobid folder

- pdftotext
    Included with most linux distributions. Is also (supposedly) part of the windows Xpdf port.

- Python3
    - lxml
        - Install lxml by running `pip install lxml`

## Usage

1. Update metadata.py to reflect new data
    - i.e. change I4A_PATH, PDF_DIR, DOC_DATE, DATE_ADDED
2. Run metadata.py
3. Output will be saved as a csv in PDF_DIR, save this csv as .xls
4. Upload papers to i4a
    - Content/Manage Files/Files/amta_paper_archive/20XX
5. Upload .xls file
    - Modules/Resource Library/Import/formatted_output.xls
