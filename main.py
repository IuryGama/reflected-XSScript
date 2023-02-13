import os
import sys
import time
import requests
import argparse

import tldextract
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin

urlChecked = []
xssPayload = "ESTOUAQUI>"
# xssPayload = "ESTOUAQUI</"
# xssPayload = "ESTOUAQUI</>"

def createHeader():
    userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"
    headers={"User-Agent": userAgent}
    return headers

def get_paths(url: str, timeout: int = 10):
    try:
        headers = createHeader()
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except (ConnectionError, Timeout, requests.exceptions.HTTPError):
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    parsed_url = urlparse(url)
    base_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    paths = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href is not None:
            parsed_link = urlparse(href)
            if parsed_link.netloc == '' or parsed_link.netloc == parsed_url.netloc or parsed_link.netloc.endswith('.' + parsed_url.netloc):
                full_url = urljoin(base_url, parsed_link.path)
                if parsed_link.query:
                    full_url += f'/?{parsed_link.query}'
                if full_url not in paths:
                    paths.append(full_url)
    return paths

def findUrl(URI: str, timeout:int = 5, result_file: str = "urls.txt"):
    # links = []
    headers=createHeader()
    
    response = requests.get(URI, headers=headers, timeout=timeout)
    soup = BeautifulSoup(response.content, 'html.parser')
    parsedUrl = urlparse(URI)
    mainDomain = tldextract.extract(URI).registered_domain
    
    for link in soup.find_all('a'):
        href = link.get('href')
        parsedLink = urlparse(href)
        linkDomain = tldextract.extract(parsedLink.netloc).registered_domain
        if linkDomain == mainDomain:
            # links.append(href)
            result = f'{href}'
            writeFile(result_file, result)
    # links = sorted(list(set(links)))
    # return links

def createEmptyURL(URI: str) -> str:
    empty_url = URI
    if "?" and "=" in URI:
        url_split = URI.split("?")
        params = url_split[1].split("&")
        
        for completeParams in params:
            if "=" in completeParams:
                splitted_param = completeParams.split("=")
                empty_url = empty_url.replace(splitted_param[0]+"="+splitted_param[1], "")
    else:
        empty_url = "NotValidURL"
    return empty_url

def forgeURL(URI: str) -> str:
    url = URI
    empty_url = createEmptyURL(URI)
    if "?" and "=" in url:
        url_split = URI.split("?")
        params = url_split[1].split("&")
        for completeParams in params:
            if "=" in completeParams:
                splitted_param = completeParams.split("=")
                url = url.replace(splitted_param[0]+"="+splitted_param[1], splitted_param[0]+"="+xssPayload+"") 
        if empty_url in urlChecked:
            print("")
        else:
            urlChecked.append(empty_url)    
    return url

def xssVerify(URI: str, timeout: int = 10, results_file: str = "xss_results.txt"):
    try:
        headers=createHeader()
        response=requests.get(URI, headers=headers, timeout=timeout)
        if response.status_code == 200:
            body=response.text
            if xssPayload in body:
                print ("[ $ ] :: XSS Vuln found in :-", URI)
                result = f"[ $ ] :: XSS Vuln found in :- {URI}\n"
                writeFile(results_file, result)
            elif xssPayload.replace(">", "") in body:
                print(xssPayload.replace(">", ""))
                # print("[ * ] :: XSS Vuln não encontrada :- ", URI)
                result = f"[ * ] :: XSS Vuln não encontrada :- {URI}"
                writeFile(results_file, result)
            else:
                print("[ X ] :: Nothig found :- ", URI)
                
    except requests.exceptions.Timeout as e:
        print("A requisição expirou")
    except requests.exceptions.HTTPError as e:
        print("Erro HTTP:", e)
    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)
    return response

def writeFile(file_name, result):
    with open(file_name, "a") as f:
        f.write(result + "\n")


# Caso tenhamos uma lista de URLs e só vamos testar o XSS        
# def main():
    # print("[ ! ] Starting....")
    # with open(urlFile, "r") as f:
        # for line in f:
            # if createEmptyURL(line.strip()) != "NotValidURL":
                # if forgeURL(line.strip()) != "NotValidURL" and "=" in forgeURL(line.strip()):
                    # xssVerify(forgeURL(line.strip()))
                    # time.sleep(50 / 1000.0)
    # return 1

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-L", help="Executa o comando passando uma lista de urls")
    parser.add_argument("-u", help="Executa o comando passando apenas uma url")
    # parser.add_argument("-o", help="Output file name")

    args = parser.parse_args()
    print("[ ! ] Starting....")

    # if args.o:
    #     output_file = open(args.o, "w")
    # else:
    #     output_file = open("output.txt", "w")

    if args.L:
        with open(args.L, "r") as f:
            for line in f:
                if createEmptyURL(line.strip()) != "NotValidURL":
                    if forgeURL(line.strip()) != "NotValidURL" and "=" in forgeURL(line.strip()):
                        xssVerify(forgeURL(line.strip()))
                        time.sleep(50 / 1000.0)
        return 1
    if args.u:
        output_file = open("output.txt", "w")
        findUrl(args.u, result_file="urls.txt")
        with open("urls.txt", "r") as f:
            for line in f:
                paths = get_paths(line.strip(), timeout=5)
                for path in paths:
                    output_file.write(path+'\n')
            output_file.close()
        print("[ ! ] Success on create files")
        return 1
    else:
        parser.print_help()
        return 0
        
main()