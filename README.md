This tool is developed for linux. Most likely it could be modified for Windows, but at the moment that is not officially supported.

Dependencies:
    - Grobid
        - For installation instructions, see: https://grobid.readthedocs.io/en/latest/Install-Grobid/
        - Should be installed in grobid folder

    - pdftotext
        Included with most linux distributions. Is also (supposedly) part of the windows Xpdf port.

    - Python3
        - lxml
            - Install lxml by running pip install lxml

Usage:
    
1) Update metadata.py to reflect new year
    - i.e. change I4A_PATH, PDF_DIR, DOC_DATE, DATE_ADDED
2) Run metadata.py
3) Output will be saved as a csv in PDF_DIR, save this csv as .xls
4) Upload papers to i4a
    i) Content/Manage Files/Files/amta_paper_archive/20XX
5) Upload .xls file
    i) Modules/Resource Library/Import/formatted_output.xls