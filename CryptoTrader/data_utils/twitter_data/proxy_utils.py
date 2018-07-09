def proxy_dict(address):
    http_proxy  = "http://{}".format(address)
    https_proxy = "https://{}".format(address)
    ftp_proxy   = "ftp://{}".format(address)

    proxyDict = { 
                  "http"  : http_proxy, 
                  "https" : https_proxy, 
                  "ftp"   : ftp_proxy
                }
    
    return proxyDict

def get_proxies():
    a = open(__file__.replace('proxy_utils.py', '') + 'proxies.txt')

    proxies = []

    for line in a.readlines():
        proxy = proxy_dict(line.replace('\n', ''))
        proxies.append(proxy)
        
    return proxies