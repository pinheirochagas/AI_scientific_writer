import os
import json
import requests
from typing import Dict, List, Any
import time

def search_pubmed(query: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Search PubMed for papers matching the query and retrieve full information including abstracts.
    
    Args:
        query: The search query string.
        max_results: Maximum number of results to retrieve.
        
    Returns:
        A list of dictionaries containing paper information.
    """
    # NCBI E-utilities base URL
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Step 1: Search for IDs matching the query
    search_url = f"{base_url}esearch.fcgi"
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": "relevance"
    }
    
    search_response = requests.get(search_url, params=search_params)
    search_data = search_response.json()
    
    if "esearchresult" not in search_data or "idlist" not in search_data["esearchresult"]:
        print("No results found or API response format unexpected")
        return []
    
    id_list = search_data["esearchresult"]["idlist"]
    
    if not id_list:
        print("No papers found matching the query")
        return []
    
    # Step 2: Fetch detailed information for each paper ID
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
        "rettype": "abstract"  # Explicitly request abstracts
    }
    
    papers = []
    
    # To avoid overwhelming the API, we'll fetch in smaller batches if needed
    batch_size = 20
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i+batch_size]
        fetch_params["id"] = ",".join(batch_ids)
        
        try:
            fetch_response = requests.get(fetch_url, params=fetch_params)
            
            if fetch_response.status_code != 200:
                print(f"Error fetching details for batch {i//batch_size + 1}: {fetch_response.status_code}")
                continue
                
            # Parse XML response to extract paper details
            xml_content = fetch_response.text
            
            # Process each PubmedArticle entry
            article_start_indices = [i for i in range(len(xml_content)) if xml_content.startswith("<PubmedArticle>", i)]
            
            for idx, start_idx in enumerate(article_start_indices):
                end_idx = xml_content.find("</PubmedArticle>", start_idx) + len("</PubmedArticle>")
                article_xml = xml_content[start_idx:end_idx]
                
                # Extract PMID
                pmid_start = article_xml.find("<PMID Version=")
                if pmid_start == -1:
                    pmid_start = article_xml.find("<PMID>")
                    if pmid_start == -1:
                        continue
                    pmid_start += len("<PMID>")
                else:
                    pmid_start = article_xml.find(">", pmid_start) + 1
                
                pmid_end = article_xml.find("</PMID>", pmid_start)
                pmid = article_xml[pmid_start:pmid_end].strip()
                
                # Extract title
                title_start = article_xml.find("<ArticleTitle>")
                title = "Title not available"
                if title_start != -1:
                    title_start += len("<ArticleTitle>")
                    title_end = article_xml.find("</ArticleTitle>", title_start)
                    title = article_xml[title_start:title_end].strip()
                
                # Extract abstract
                abstract = "Abstract not available"
                abstract_start = article_xml.find("<AbstractText")
                if abstract_start != -1:
                    # Handle potential attributes in the AbstractText tag
                    abstract_start = article_xml.find(">", abstract_start) + 1
                    abstract_end = article_xml.find("</AbstractText>", abstract_start)
                    abstract = article_xml[abstract_start:abstract_end].strip()
                
                # Extract authors
                authors = []
                author_list_start = article_xml.find("<AuthorList")
                if author_list_start != -1:
                    author_list_end = article_xml.find("</AuthorList>", author_list_start)
                    author_list = article_xml[author_list_start:author_list_end]
                    
                    author_start_indices = [i for i in range(len(author_list)) if author_list.startswith("<Author ", i) or author_list.startswith("<Author>", i)]
                    
                    for author_idx in author_start_indices:
                        author_end = author_list.find("</Author>", author_idx)
                        author_xml = author_list[author_idx:author_end]
                        
                        last_name = ""
                        last_name_start = author_xml.find("<LastName>")
                        if last_name_start != -1:
                            last_name_start += len("<LastName>")
                            last_name_end = author_xml.find("</LastName>", last_name_start)
                            last_name = author_xml[last_name_start:last_name_end].strip()
                        
                        first_name = ""
                        first_name_start = author_xml.find("<ForeName>")
                        if first_name_start != -1:
                            first_name_start += len("<ForeName>")
                            first_name_end = author_xml.find("</ForeName>", first_name_start)
                            first_name = author_xml[first_name_start:first_name_end].strip()
                        
                        if last_name or first_name:
                            authors.append(f"{last_name}{', ' + first_name if first_name else ''}")
                
                # Extract year
                year = "Year not available"
                year_start = article_xml.find("<PubDate>")
                if year_start != -1:
                    year_tag_start = article_xml.find("<Year>", year_start)
                    if year_tag_start != -1:
                        year_start = year_tag_start + len("<Year>")
                        year_end = article_xml.find("</Year>", year_start)
                        year = article_xml[year_start:year_end].strip()
                
                # Extract journal
                journal = "Journal not available"
                journal_start = article_xml.find("<Journal>")
                if journal_start != -1:
                    title_start = article_xml.find("<Title>", journal_start)
                    if title_start != -1:
                        title_start += len("<Title>")
                        title_end = article_xml.find("</Title>", title_start)
                        journal = article_xml[title_start:title_end].strip()
                
                paper = {
                    "pmid": pmid,
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "journal": journal,
                    "abstract": abstract
                }
                
                papers.append(paper)
            
            # Be nice to the API with a short delay between batches
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {str(e)}")
    
    return papers

def run_pubmed_agent(query: str, output_path: str) -> str:
    """
    Run the PubMed search agent and save results to a JSON file.
    
    Args:
        query: The search query string.
        output_path: Path to save the JSON results.
        
    Returns:
        Path to the saved JSON file.
    """
    print(f"Searching PubMed for: {query}")
    papers = search_pubmed(query)
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save results to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(papers)} papers matching the query. Results saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Test the agent
    test_query = "Maria Luisa Gorno-Tempini AND PPA"
    test_output = "test_pubmed_results.json"
    run_pubmed_agent(test_query, test_output)