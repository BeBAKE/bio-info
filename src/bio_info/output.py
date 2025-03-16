"""
Module for generating output CSV from paper data.
"""

import csv
import sys
import logging
from typing import Dict, List, TextIO, Any

import pandas as pd

logger = logging.getLogger(__name__)

def format_output_data(papers_with_company_authors: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    output_data = []
    
    for paper in papers_with_company_authors:
        output_data.append({
            "PubmedID": paper["pubmed_id"],
            "Title": paper["title"],
            "Publication Date": paper["publication_date"],
            "Non-academic Author(s)": "; ".join(paper["non_academic_authors"]),
            "Company Affiliation(s)": "; ".join(paper["company_affiliations"]),
            "Corresponding Author Email": paper["corresponding_email"]
        })
    
    return output_data

def write_csv(data: List[Dict[str, str]], file_path: str) -> None:
    if not data:
        logger.warning("No data to write to CSV")
        return
        
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        logger.info(f"Successfully wrote data to {file_path}")
    except Exception as e:
        logger.error(f"Error writing CSV to {file_path}: {e}")
        raise

def print_csv(data: List[Dict[str, str]]) -> None:
    if not data:
        logger.warning("No data to print as CSV")
        return
        
    try:
        df = pd.DataFrame(data)
        print(df.to_csv(index=False))
    except Exception as e:
        logger.error(f"Error printing CSV: {e}")
        raise