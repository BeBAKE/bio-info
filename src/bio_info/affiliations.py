"""
Module for identifying non-academic authors based on their affiliations.
"""

import re
import logging
from typing import Dict, List, Tuple, Set

logger = logging.getLogger(__name__)

# Keywords indicating academic institutions
ACADEMIC_KEYWORDS = {
    "university", "college", "institute", "school", "academy", "campus",
    "polytechnic", "medical center", "medical school", "hospital", 
    "clinic", "foundation", "laboratory", "research center", "national",
    "federal", "ministry", "department", "government", "agency"
}

# Keywords indicating pharmaceutical/biotech companies
PHARMA_BIOTECH_KEYWORDS = {
    "pharma", "pharmaceutical", "biotech", "biologics", "therapeutics",
    "drugs", "medicines", "bioscience", "life sciences", "biopharmaceutical",
    "diagnostics", "pharmaceuticals", "laboratories", "labs", "inc", "llc",
    "corp", "corporation", "ltd", "limited", "gmbh", "co", "company"
}

# Email domains suggesting companies
COMPANY_EMAIL_DOMAINS = {
    ".com", ".co", ".io", ".ai", ".bio", ".health", ".pharma", ".tech"
}

# Email domains suggesting academic institutions
ACADEMIC_EMAIL_DOMAINS = {
    ".edu", ".ac.", ".sch."
}

def is_likely_company(text: str) -> bool:
    text_lower = text.lower()
    
    # Check for pharmaceutical/biotech keywords
    for keyword in PHARMA_BIOTECH_KEYWORDS:
        if keyword in text_lower:
            return True
            
    # Check for pattern like "Company Name, Inc." or "Company Name Ltd."
    company_pattern = r'(?:inc|llc|corp|ltd|gmbh|co|company)[\.\,]?\s*$'
    if re.search(company_pattern, text_lower):
        return True
        
    return False

def is_likely_academic(text: str) -> bool:
    text_lower = text.lower()
    
    for keyword in ACADEMIC_KEYWORDS:
        if keyword in text_lower:
            return True
            
    return False

def is_company_email(email: str) -> bool:
    if not email or "@" not in email:
        return False
        
    domain = email.split("@")[1].lower()
    
    # Check for academic domains first
    for academic_domain in ACADEMIC_EMAIL_DOMAINS:
        if academic_domain in domain:
            return False
            
    # Check for company domains
    for company_domain in COMPANY_EMAIL_DOMAINS:
        if domain.endswith(company_domain):
            return True
            
    return False

def identify_company_authors(paper: Dict) -> Tuple[List[str], List[str], str]:
    non_academic_authors = []
    company_affiliations = set()
    corresponding_email = ""
    
    for author in paper.get("authors", []):
        is_non_academic = False
        
        # Check affiliations
        for affiliation in author.get("affiliations", []):
            if is_likely_company(affiliation) and not is_likely_academic(affiliation):
                is_non_academic = True
                company_name = extract_company_name(affiliation)
                if company_name:
                    company_affiliations.add(company_name)
        
        # Check email domain
        if is_company_email(author.get("email", "")):
            is_non_academic = True
        
        if is_non_academic:
            non_academic_authors.append(author["name"])
        
        # Track corresponding author email
        if author.get("is_corresponding", False) and author.get("email"):
            corresponding_email = author["email"]
    
    return non_academic_authors, list(company_affiliations), corresponding_email

def extract_company_name(affiliation: str) -> str:
    # Try to extract company name using common patterns
    company_patterns = [
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Inc\.?)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+LLC)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Ltd\.?)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Corp\.?)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+GmbH)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Pharma)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Pharmaceuticals)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Biotech)',
        r'([A-Z][A-Za-z0-9\s\&\-\.]{2,50})(?:,?\s+Therapeutics)'
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, affiliation)
        if match:
            return match.group(1).strip()
    
    # If no match found, return the first part of the affiliation
    # which might be the company name
    parts = affiliation.split(',')
    if parts:
        company = parts[0].strip()
        # Only return if it looks like a company name (starts with capital letter)
        if re.match(r'^[A-Z]', company) and len(company) > 3:
            return company
            
    return ""