import httpx
from bs4 import BeautifulSoup
from markdownify import markdownify

async def scrape_jd_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        
    soup = BeautifulSoup(resp.text, 'lxml')
    # Strip unnecessary elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()
        
    markdown_text = markdownify(str(soup), heading_style="ATX")
    return markdown_text.strip()
