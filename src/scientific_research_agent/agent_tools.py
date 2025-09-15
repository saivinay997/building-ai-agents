import io
import time
import ssl
import urllib3
from urllib3.util.ssl_ import create_urllib3_context
from langchain_core.tools import BaseTool, tool
from scientific_research_agent.pydantic_models import SearchPapersInput
from scientific_research_agent.core_api_wrapper import CoreAPIWrapper
import pdfplumber

# Suppress SSL warnings for scientific paper downloads
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@tool("search-paper", args_schema=SearchPapersInput)
def search_paper(query: str, max_papers: int = 1) -> str:
    """Search for scientific papers using the CORE API.
    Example:
    { "query": "Attention is all you neeed", "max_papers": 1 }
    
    Returns:
        A list of the relevant papers found with the corresponding relevant information.
    """
    try:
        papers = CoreAPIWrapper(top_k_results=max_papers).search(query)
        print("Search paper tool output:", papers)
        return papers
    except Exception as e:
        return f"Error searching for papers: {e}"
    
@tool("download-paper")
def download_paper(url: str) -> str:
    """Download a specific scientific paper from a given URL.
    Example:
     { "url": "https://www.example.com/paper.pdf" }
     
     Returns:
         the paper content
    
    """
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        return f"Error: Invalid URL format. URL must start with http:// or https://. Got: {url}"
    
    # Create SSL context that's more permissive for scientific repositories
    ssl_context = create_urllib3_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Create HTTP pool manager with custom SSL context
    http = urllib3.PoolManager(
        ssl_context=ssl_context,
        cert_reqs='CERT_NONE',
        assert_hostname=False
    )
    
    # Mock browser headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = http.request('GET', url, headers=headers)
            
            # Check HTTP status
            if response.status == 200:
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                
                # Check if response is actually a PDF
                if 'application/pdf' in content_type or url.lower().endswith('.pdf'):
                    try:
                        pdf_file = io.BytesIO(response.data)
                        with pdfplumber.open(pdf_file) as pdf:
                            if len(pdf.pages) == 0:
                                return "Error: PDF file appears to be empty or corrupted (no pages found)."
                            
                            text = ""
                            for page_num, page in enumerate(pdf.pages, 1):
                                page_text = page.extract_text()
                                if page_text:
                                    text += page_text + "\n"
                                else:
                                    text += f"[Page {page_num}: No text content found]\n"
                            
                            if not text.strip():
                                return "Error: PDF file could not be processed - no text content could be extracted."
                            
                            return text
                            
                    except Exception as pdf_error:
                        # Check if the response is actually HTML (common with redirects)
                        response_text = response.data.decode('utf-8', errors='ignore')
                        if response_text.strip().startswith('<'):
                            return f"Error: URL redirected to HTML page instead of PDF. This often happens with paywalled or restricted papers. URL: {url}"
                        else:
                            return f"Error: Failed to process PDF file. The file may be corrupted or not a valid PDF. Error: {str(pdf_error)}"
                
                else:
                    # Check if response is HTML (common with redirects or error pages)
                    response_text = response.data.decode('utf-8', errors='ignore')
                    if response_text.strip().startswith('<'):
                        return f"Error: URL returned HTML content instead of PDF. Content-Type: {content_type}. This often indicates the paper is behind a paywall or requires authentication. URL: {url}"
                    else:
                        return f"Error: URL did not return a PDF file. Content-Type: {content_type}. URL: {url}"
            
            elif response.status == 403:
                return f"Error: Access forbidden (HTTP 403). The paper may be behind a paywall or require authentication. URL: {url}"
            
            elif response.status == 404:
                return f"Error: Paper not found (HTTP 404). The URL may be incorrect or the paper may have been moved. URL: {url}"
            
            elif response.status == 429:
                return f"Error: Too many requests (HTTP 429). Please try again later. URL: {url}"
            
            else:
                return f"Error: HTTP {response.status} - {response.reason}. URL: {url}"
                
        except Exception as e:
            if attempt == max_retries - 1:
                return f"Error downloading paper after {max_retries} attempts: {str(e)}. URL: {url}"
            time.sleep(2**attempt)
    
    return f"Error: Failed to download paper after {max_retries} attempts. URL: {url}"

@tool("ask-human-feedback")
def ask_human_feedback(question: str) -> str:
    """Ask for human feedback. You should call this tool when encountering unexpected errors."""
    return input(question)

@tool("suggest-alternative-sources")
def suggest_alternative_sources(paper_title: str = "", paper_doi: str = "") -> str:
    """Suggest alternative sources when a paper cannot be downloaded from the original URL.
    
    Args:
        paper_title: The title of the paper (optional)
        paper_doi: The DOI of the paper (optional)
    
    Returns:
        Suggestions for alternative ways to access the paper
    """
    suggestions = [
        "Alternative sources to try:",
        "1. **arXiv**: Check if the paper is available on arXiv.org (free access)",
        "2. **PubMed Central (PMC)**: Look for open access versions",
        "3. **Google Scholar**: Search for the paper title to find alternative sources",
        "4. **ResearchGate**: Academic social network with many papers",
        "5. **Academia.edu**: Another academic platform",
        "6. **Institutional repositories**: Check the author's university repository",
        "7. **Author's personal website**: Many researchers post their papers",
        "8. **Contact the authors**: Email the corresponding author for a copy",
        "",
        "Common issues and solutions:",
        "- **Paywall**: The paper may be behind a paywall. Try open access alternatives.",
        "- **Institutional access**: You may need to access through a university library.",
        "- **DOI resolution**: Try using the DOI directly in a DOI resolver.",
        "- **Preprint versions**: Look for preprint versions on arXiv or bioRxiv.",
        "",
        "If you have the paper title or DOI, I can help you search for alternative sources."
    ]
    
    if paper_title:
        suggestions.append(f"\nFor the paper '{paper_title}', try searching:")
        suggestions.append(f"- arXiv: https://arxiv.org/search/?query={paper_title.replace(' ', '+')}")
        suggestions.append(f"- Google Scholar: https://scholar.google.com/scholar?q={paper_title.replace(' ', '+')}")
    
    if paper_doi:
        suggestions.append(f"\nFor DOI {paper_doi}:")
        suggestions.append(f"- DOI resolver: https://doi.org/{paper_doi}")
        suggestions.append(f"- Unpaywall: https://unpaywall.org/")
    
    return "\n".join(suggestions)

tools = [search_paper, download_paper, suggest_alternative_sources]
tools_dict = {tool.name: tool for tool in tools}
    
def format_tool_description(tools: list[BaseTool]) -> str:
    """Format the tool description for the planning node."""
    return "\n".join([f"- {tool.name}: {tool.description} \n Input arguments: {tool.args}" for tool in tools])
    