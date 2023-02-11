import os
import sys
import time
import requests

urlChecked = []
urlFile = sys.argv[1]
xssPayload = "ESTOUAQUI>"
# xssPayload = "ESTOUAQUI</"
# xssPayload = "ESTOUAQUI</>"
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78"

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
        headers={"User-Agent": userAgent}
        response=requests.get(URI, headers=headers, timeout=timeout)
        if response.status_code == 200:
            body=response.text
            if xssPayload in body:
                print ("[ $ ] :: XSS Vuln found in :-", URI)
                result = f"[ $ ] :: XSS Vuln found in :- {URI}\n"
                writeFile(results_file, result)
                # criar arquivo XSSresults.txt
                # with open("XSSresults.txt", "a") as f:
                    # f.write("[ $ ] XSS Vuln :: " + URI + "\n")
            elif xssPayload.replace(">", "") in body:
                print("[ * ] :: XSS Vuln não encontrada :- ", URI)
                result = f"[ * ] :: XSS Vuln não encontrada :- {URI}"
                writeFile(results_file, result)
                # with open("XSSresults.txt", "a") as f:
                    # f.write("[ * ] Reflection :: " + URI + "\n")
            else:
                print("[X] :: Nothig found :- ", URI)
                
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
        
def main():
    print("[ ! ] Starting....")
    with open(urlFile, "r") as f:
        for line in f:
            if createEmptyURL(line.strip()) != "NotValidURL":
                if forgeURL(line.strip()) != "NotValidURL" and "=" in forgeURL(line.strip()):
                    xssVerify(forgeURL(line.strip()))
                    time.sleep(50 / 1000.0)
    return 1

main()