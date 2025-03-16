"""
API module for fetching data from PubMed.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import time
import requests
from Bio import Entrez

# Configure logging
logger = logging.getLogger(__name__)

class PubMedAPI:
    
    def __init__(self, email: str = "your.email@example.com", tool: str = "pubmed-papers"):
        Entrez.email = email
        Entrez.tool = tool
        
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        logger.debug(f"Searching PubMed with query: {query}")
        try:
            # Search PubMed
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()
            
            pubmed_ids = record["IdList"]
            logger.debug(f"Found {len(pubmed_ids)} papers")
            
            return pubmed_ids
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str, Any]]:
        if not pubmed_ids:
            return []
        
        logger.debug(f"Fetching details for {len(pubmed_ids)} papers")
        papers = []
        
        try:
            # Fetch details in batches of 50 to avoid overloading the API
            batch_size = 50
            for i in range(0, len(pubmed_ids), batch_size):
                batch_ids = pubmed_ids[i:i+batch_size]
                handle = Entrez.efetch(db="pubmed", id=",".join(batch_ids), retmode="xml")
                records = Entrez.read(handle)
                handle.close()
                
                for record in records["PubmedArticle"]:
                    try:
                        paper = self._parse_paper_record(record)
                        papers.append(paper)
                    except Exception as e:
                        pubmed_id = record["MedlineCitation"]["PMID"]
                        logger.error(f"Error parsing paper {pubmed_id}: {e}")
                
                # Be nice to the API with a small delay between batches
                if i + batch_size < len(pubmed_ids):
                    time.sleep(0.5)
                    
            return papers
        except Exception as e:
            logger.error(f"Error fetching paper details: {e}")
            raise
            
    def _parse_paper_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        article = record["MedlineCitation"]["Article"]
        pubmed_id = record["MedlineCitation"]["PMID"]
        
        # Extract title
        title = article.get("ArticleTitle", "")
        
        # Extract publication date
        try:
            pub_date_parts = []
            if "PubDate" in article["Journal"]["JournalIssue"]["PubDate"]:
                pub_date = article["Journal"]["JournalIssue"]["PubDate"]
                if "Year" in pub_date:
                    pub_date_parts.append(pub_date["Year"])
                if "Month" in pub_date:
                    pub_date_parts.append(pub_date["Month"])
                if "Day" in pub_date:
                    pub_date_parts.append(pub_date["Day"])
            publication_date = "/".join(pub_date_parts) if pub_date_parts else ""
        except (KeyError, TypeError):
            publication_date = ""
        
        # Extract authors and affiliations
        authors = []
        if "AuthorList" in article:
            for author in article["AuthorList"]:
                if "LastName" in author and "ForeName" in author:
                    name = f"{author.get('LastName', '')}, {author.get('ForeName', '')}"
                    
                    # Extract affiliations
                    affiliations = []
                    if "AffiliationInfo" in author:
                        for affiliation in author["AffiliationInfo"]:
                            if "Affiliation" in affiliation:
                                affiliations.append(affiliation["Affiliation"])
                                
                    # Extract email
                    email = ""
                    if "Identifier" in author:
                        for identifier in author["Identifier"]:
                            if identifier.attributes.get("Source") == "ORCID":
                                continue
                            if "@" in identifier:
                                email = identifier
                                break
                            
                    authors.append({
                        "name": name,
                        "affiliations": affiliations,
                        "email": email,
                        "is_corresponding": False  # Will update later
                    })
        
        # Try to find corresponding author
        if "ELocationID" in article:
            for location in article["ELocationID"]:
                if location.attributes.get("EIdType") == "email":
                    # Found an email, try to match it to an author
                    corresponding_email = location
                    for author in authors:
                        if author["email"] == corresponding_email:
                            author["is_corresponding"] = True
                            break
        
        return {
            "pubmed_id": pubmed_id,
            "title": title,
            "publication_date": publication_date,
            "authors": authors
        }
    