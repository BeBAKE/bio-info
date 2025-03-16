
"""
Tests for the bio_info package.
"""

import pytest
from unittest.mock import patch, MagicMock

from bio_info.api import PubMedAPI
from bio_info.affiliations import (
    is_likely_company,
    is_likely_academic,
    is_company_email,
    identify_company_authors
)
from bio_info.output import format_output_data

def test_is_likely_company():
    """Test company detection."""
    assert is_likely_company("Pfizer Inc.") is True
    assert is_likely_company("Novartis Pharmaceuticals") is True
    assert is_likely_company("GeneTech Biotech Corp") is True
    assert is_likely_company("University of California") is False

def test_is_likely_academic():
    """Test academic institution detection."""
    assert is_likely_academic("Stanford University") is True
    assert is_likely_academic("Harvard Medical School") is True
    assert is_likely_academic("National Institute of Health") is True
    assert is_likely_academic("AstraZeneca Inc.") is False

def test_is_company_email():
    """Test company email detection."""
    assert is_company_email("john.doe@pharma.com") is True
    assert is_company_email("researcher@biotech.io") is True
    assert is_company_email("scientist@university.edu") is False

def test_identify_company_authors():
    """Test identification of non-academic authors."""
    test_paper = {
        "pubmed_id": "12345678",
        "title": "Test Paper",
        "publication_date": "2023/01/15",
        "authors": [
            {
                "name": "Smith, John",
                "affiliations": ["Harvard University", "Stanford Medical School"],
                "email": "smith@harvard.edu",
                "is_corresponding": False
            },
            {
                "name": "Doe, Jane",
                "affiliations": ["Pfizer Inc.", "New York, USA"],
                "email": "jane.doe@pfizer.com",
                "is_corresponding": True
            }
        ]
    }
    
    non_academic_authors, company_affiliations, corresponding_email = identify_company_authors(test_paper)
    
    assert "Doe, Jane" in non_academic_authors
    assert "Smith, John" not in non_academic_authors
    assert "Pfizer" in company_affiliations[0]
    assert corresponding_email == "jane.doe@pfizer.com"

def test_format_output_data():
    """Test formatting of output data."""
    test_papers = [
        {
            "pubmed_id": "12345678",
            "title": "Test Paper 1",
            "publication_date": "2023/01/15",
            "non_academic_authors": ["Doe, Jane", "Smith, Bob"],
            "company_affiliations": ["Pfizer Inc.", "Moderna"],
            "corresponding_email": "jane.doe@pfizer.com"
        }
    ]
    
    output = format_output_data(test_papers)
    
    assert len(output) == 1
    assert output[0]["PubmedID"] == "12345678"
    assert output[0]["Title"] == "Test Paper 1"
    assert output[0]["Publication Date"] == "2023/01/15"
    assert output[0]["Non-academic Author(s)"] == "Doe, Jane; Smith, Bob"
    assert output[0]["Company Affiliation(s)"] == "Pfizer Inc.; Moderna"
    assert output[0]["Corresponding Author Email"] == "jane.doe@pfizer.com"

@patch('bio_info.api.Entrez')
def test_search_papers(mock_entrez):
    """Test PubMed search functionality."""
    # Mock Entrez.esearch response
    mock_handle = MagicMock()
    mock_record = {"IdList": ["12345678", "87654321"]}
    mock_entrez.esearch.return_value = mock_handle
    mock_entrez.read.return_value = mock_record
    
    api = PubMedAPI()
    result = api.search_papers("test query")
    
    assert mock_entrez.esearch.called
    assert len(result) == 2
    assert "12345678" in result