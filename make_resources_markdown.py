"""Generates a markdown document for resources"""

import biblib.bib # as bib
import sys
import re


qmd_header = """---
title: Resources
date: last-modified
bibliography: references.bib
---

"""

# List of tags for different sections
GENERAL_OPEN_SCIENCE = [
    "gentemann_why_2023",
    "lowndes_open_2019",
    "tops_guide",
    "heise_ten_2023",
    "urai_rethinking_2023",
    "whostp_yos_2023",
    ]

OPEN_PUBLICATIONS = [
    "parsons_credit_2022",
    ]

OPEN_DATA = [
    "adc_fundamentals_2022",
    "wickham_tidy_2014",
    "nsfdl_open_data_2022",
    ]

REPRODUCIBLE_RESEARCH = [
    "wilson_best_2014",
    "wilson_good_2017",
    "rodrigues_building_2023",
    ]

def parse_authorlist(author_list):
    """Parses the list of authors from bibtex and returns an APA style author list"""
    if author_list is None:
        return
    if not re.match("[A-Z]\S+, [A-Z]\S+( and [A-Z]\S+, [A-Z]\S+)*", author_list):
        return author_list
    authors = [parse_author(author) for author in author_list.split(' and ')]
    if len(authors) == 1:
        return authors[0]
    return ', & '.join([', '.join(authors[:-1]), authors[-1]])


def parse_author(author):
    """Parses a single author and returns lastname, first_initial, second_initial..."""
    lastname, firstnames = author.split(',')
    return ', '.join([lastname, parse_firstname(firstnames)])


def parse_firstname(firstname):
    """Returns a list of initials from firstname field"""
    names = [f"{c[0]}." for c in firstname.split()]
    return ' '.join(names)


def get_bibtex_db():
    """Loads a bibtex file"""
    with open('references.bib') as f:
        db = biblib.bib.Parser().parse(f, log_fp=sys.stderr).get_entries()
    return db


def make_citation(ent):
    """Create a citation in APA style"""
    result = []
    for field in ['author', 'year', 'title', 'journal', 'volume', 'doi']:
        if field == 'author':
            result.append(parse_authorlist(ent.get(field)))
        elif field == 'doi':
            if 'doi' not in ent:
                result.append(ent.get('url'))
                result.append(f"accessed: {ent.get('urldate')}")
            else:
                result.append(ent.get(field))
        else:
            result.append(ent.get(field))
    return ', '.join([x for x in result if x is not None])


def create_doi_link(ent):
    if "doi" in ent:
        return f"https://doi.org/{ent.get('doi')}"
    else:
        return ""


def create_resource(tag, ent):
    """Generates a resource entry"""
    result = ""
    result += f"**Title:** {ent.get('title')}  \n\n"
    for field in ['author', 'year', 'annotation', 'url', 'doi']:
        if field == 'author':
            result += f"* **{field.title()}:** {parse_authorlist(ent.get(field, ''))}  \n"
        elif field == "doi":
            result += f"* **{field.title()}:** {create_doi_link(ent)} \n"
        else:
            result += f"* **{field.title()}:** {ent.get(field, '')}  \n"

    result += f"* **Citation:** {make_citation(ent)}\n"
    result += "\n"
    return result


def main():
    """Create qmd files"""
    db = get_bibtex_db()
    
    # Add entry keys for different sections
    with open('resources_entries.qmd', 'w') as of:
        of.write(qmd_header)

        of.write("## General Reading\n\n")
        for tag in GENERAL_OPEN_SCIENCE:
            of.write(f"{create_resource(tag, db[tag])}\n")

        of.write("## Reproducible Research\n\n")
        for tag in REPRODUCIBLE_RESEARCH:
            of.write(f"{create_resource(tag, db[tag])}\n")

        of.write("## Open Access Publishing\n\n")
        for tag in OPEN_PUBLICATIONS:
            of.write(f"{create_resource(tag, db[tag])}\n")

        of.write("## Open Data\n\n")
        for tag in OPEN_DATA:
            of.write(f"{create_resource(tag, db[tag])}\n")

        #for tag, ent in db.items():
        #    of.write(f"{create_resource(tag, ent)}\n")


if __name__ == "__main__":
    main()
