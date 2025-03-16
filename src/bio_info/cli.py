"""
Command-line interface for the pubmed-papers tool.
"""

import argparse
import logging
import sys
from typing import List, Dict, Any, Optional

from bio_info.api import PubMedAPI
from bio_info.affiliations import identify_company_authors
from bio_info.output import format_output_data, write_csv, print_csv

def setup_logging(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch research papers with authors from pharmaceutical/biotech companies from PubMed"
    )
    
    parser.add_argument(
        "query",
        help="PubMed search query (enclose in quotes for complex queries)"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Filename to save results (if not provided, print to console)",
        default=None
    )
    
    parser.add_argument(
        "-d", "--debug",
        help="Print debug information during execution",
        action="store_true"
    )
    
    parser.add_argument(
        "-m", "--max-results",
        help="Maximum number of results to fetch from PubMed (default: 100)",
        type=int,
        default=100
    )
    
    return parser.parse_args()

def process_papers(api: PubMedAPI, query: str, max_results: int = 100) -> List[Dict[str, Any]]:
    logging.info(f"Searching for papers with query: {query}")
    
    # Search PubMed
    pubmed_ids = api.search_papers(query, max_results)
    
    if not pubmed_ids:
        logging.warning("No papers found for the given query")
        return []
    
    # Fetch paper details
    papers = api.fetch_paper_details(pubmed_ids)
    
    logging.info(f"Found {len(papers)} papers, filtering for non-academic authors")
    
    # Filter for papers with non-academic authors
    papers_with_company_authors = []
    
    for paper in papers:
        non_academic_authors, company_affiliations, corresponding_email = identify_company_authors(paper)
        
        if non_academic_authors:
            papers_with_company_authors.append({
                "pubmed_id": paper["pubmed_id"],
                "title": paper["title"],
                "publication_date": paper["publication_date"],
                "non_academic_authors": non_academic_authors,
                "company_affiliations": company_affiliations,
                "corresponding_email": corresponding_email
            })
    
    logging.info(f"Found {len(papers_with_company_authors)} papers with non-academic authors")
    
    return papers_with_company_authors

def main() -> None:
    """Main entry point for the command-line program."""
    args = parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    
    try:
        # Initialize API client
        api = PubMedAPI()
        
        # Process papers
        papers_with_company_authors = process_papers(api, args.query, args.max_results)
        
        if not papers_with_company_authors:
            logging.warning("No papers with non-academic authors found")
            return
        
        # Format output data
        output_data = format_output_data(papers_with_company_authors)
        
        # Output results
        if args.file:
            write_csv(output_data, args.file)
        else:
            print_csv(output_data)
            
    except Exception as e:
        logging.error(f"Error processing papers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()