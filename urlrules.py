import sys
import requests
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urlparse

url = "" # url = sys.argv[1]

def createHeader():
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
    headers={"User-Agent": userAgent}
    return headers

def findUrl(URI: str, timeout:int = 10, result_file: str = "urls.txt"):
    links = []
    headers=createHeader()
    
    response = requests.get(URI, headers=headers, timeout=timeout)
    soup = BeautifulSoup(response.content, 'html.parser')
    parsedUrl = urlparse(URI)
    mainDomain = tldextract.exctract(URI).registeredDomain
    
    for link in soup.find_all('a'):
        href = link.get('href')
        parsedLink = urlparse('href')
        linkDomain = tldextract.extract(parsedLink.netloc).registered_domain
        if linkDomain == mainDomain:
            link.append(href)
    links = sorted(list(set(links)))
    
"""
import requests
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urlparse

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"

# URL da página para coletar links
url = 'https://inf.ufes.br'

# Lista para armazenar links de domínios e subdomínios
links = []

# Monta o cabeçalho da requisição
headers={"User-Agent": userAgent}
# Fazer solicitação HTTP para a página da web
response = requests.get(url, headers=headers, timeout=10)

# Analisar o HTML da página com BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Extrair o domínio e subdomínio da página original
parsed_url = urlparse(url)
main_domain = tldextract.extract(url).registered_domain

# Encontrar todos os elementos <a> na página
for link in soup.find_all('a'):
    # Extrair o valor do atributo href
    href = link.get('href')
    # Analisar o link com urllib.parse
    parsed_link = urlparse(href)
    # Extrair o domínio e subdomínio do link com tldextract
    link_domain = tldextract.extract(parsed_link.netloc).registered_domain
    # Comparar o domínio e subdomínio do link com o domínio da página original
    if link_domain == main_domain:
        # Adicionar o link à lista se pertencer ao domínio principal
        links.append(href)

# Remover duplicatas e ordenar a lista
links = sorted(list(set(links)))

# Imprimir a lista de links de domínios e subdomínios que pertencem ao domínio principal
print(links)
"""
