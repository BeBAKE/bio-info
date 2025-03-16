# Bio-Info

A Python tool to fetch research papers from PubMed and identify those with authors affiliated with pharmaceutical or biotech companies.

## Features

- Search PubMed using the full PubMed query syntax
- Identify papers with authors affiliated with pharmaceutical or biotech companies
- Extract corresponding author emails
- Output results to CSV or console

## Code Organization

The project is organized as follows:

- `bio_info/`: Main package directory
  - `__init__.py`: Package initialization
  - `api.py`: Module for interacting with the PubMed API
  - `affiliations.py`: Module for identifying non-academic authors and company affiliations
  - `output.py`: Module for generating and formatting CSV output
  - `cli.py`: Command-line interface implementation
- `tests/`: Test directory
  - `test_bio_info.py`: Unit tests for the package

## Installation

This project uses Poetry for dependency management.

1. Make sure you have Python 3.8+ and Poetry installed
2. Clone the repository

```bash
git clone https://github.com/yourusername/pubmed-papers.git
cd pubmed-papers
```

3. Install dependencies

```bash
poetry install
```

## Usage

After installation, you can use the `get-papers-list` command to search for papers:

```bash
# Basic usage, prints results to console
poetry run get-papers-list "cancer therapy"

# Save results to a CSV file
poetry run get-papers-list "artificial intelligence AND medicine" -f results.csv

# Enable debug mode
poetry run get-papers-list "COVID-19 vaccine" -d

# Limit results (default is 100)
poetry run get-papers-list "gene therapy" -m 50
```

### Command Line Arguments

- `query`: PubMed search query (enclose in quotes for complex queries)
- `-h, --help`: Show help message and exit
- `-f, --file`: Specify the filename to save the results (if not provided, print to console)
- `-d, --debug`: Print debug information during execution
- `-m, --max-results`: Maximum number of results to fetch from PubMed (default: 100)

## Dependencies

This project uses the following key libraries:

- [Biopython](https://biopython.org/): For accessing the PubMed API
- [Pandas](https://pandas.pydata.org/): For data manipulation and CSV handling
- [Requests](https://requests.readthedocs.io/): For HTTP requests

## Development

### Running Tests

```bash
poetry run pytest
```

### Tools Used

The following tools were used in the development of this project:

- [Poetry](https://python-poetry.org/): Dependency management
- [Pytest](https://pytest.org/): Testing framework
- [Black](https://black.readthedocs.io/): Code formatting
- [MyPy](https://mypy.readthedocs.io/): Static type checking
