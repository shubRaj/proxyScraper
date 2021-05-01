import scrapy,re,json
from urllib.parse import urlparse,parse_qs
"""
Get rotating ip at :- https://proxy.webshare.io

"""
# from port_checker import port_checker

# def get_proxy():
#     with open("proxyConf.json") as proxies:
#         proxies = [{"ip":proxy.get('ip'),"port":proxy.get('port')} for proxy in json.load(proxies) if proxy.get("protocol").startswith("http")]
#     for proxy in proxies:
#         print(proxy)
#         if port_checker(proxy.get("ip"),int(proxy.get("port"))):
#             break
#     return f'{proxy.get("ip")}:{proxy.get("port")}'
def _base(original):
    def wrapper(*args,**kwargs):
        response = args[1]
        if response.status == 200:
            proxies = [proxy for proxy in original(*args,**kwargs)]
            yield from proxies
        return original(*args,**kwargs)
    return wrapper
class ProxySpider(scrapy.Spider):
    name = "proxy"
    def start_requests(self):
        urls = [
            "https://www.sslproxies.org/",
            "https://free-proxy-list.net/anonymous-proxy.html",
            "https://free-proxy-list.net/uk-proxy.html",
            "https://www.us-proxy.org/",
            "https://free-proxy-list.net/",
        ]
        http_country_codes = (
            "DE",
            "ZA",
            "US",
            "CN",
            "TR",
            "JP",
            "UA",
            "SG",
            "RU",
            "GB",
            "BD",
            "PK",
            "IN",
            "BR",
            "TH",
            "ID",
            "EC",
            "CO",
            "MX",
            "FR",
            "CA",
            "NP",
            "KR",
            "PE",
            "AR",
            "IR",
            "VN",
            "NG",
            "KH"
        )
        socks4_country_code = (
            "UA",
            "CA",
            "BG",
            "IR",
            "IN",
            "RU",
            "KH",
            "BR",
            "ID",
            "CO",
            "US",
            "ZA",
            "FI",
            "MX",
            "CL",
            "BD",
            "RO",
            "LV",
            "PS",
            "TH",
            "BO",
            "TR",
            "NG",
            "HU",
            "CN",
            "AR",
            "NP",
            "VN",
            "HR",
            "SY",
            "SG",
            "EC",
            "TW",
            "GB",
            "GE",
            "IQ",
            "AL",
            "PL",
            "CR",
            "KR",
            "CZ",
            "SK",
            "DE",
            "ES",
            "PK",
            "NL",
            "MN",
            "MY",
            "PA",
            "AM",
            "HN",
            "RS",
            "KZ",
            "IT",
            "AT",
            "PH",
            "VE",
            "KE",
            "FR",
        )
        socks5_country_code = (
            "US",
            "UA",
            "IN",
            "DE",
            "FI",
            "CN",
            "RU",
            "AR",
            "SG",
            "FR",
        )
        anonymities = (
            "elite","anonymous","transparent"
        )
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse_sslproxies)
        yield scrapy.Request(url="http://spys.me/proxy.txt",callback=self.parse_spysme_txt)
        for http_country in http_country_codes:
            for anonymity in anonymities:
                for ssl in ("yes","no"):
                    yield scrapy.Request(url=f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country={http_country}&ssl={ssl}&anonymity={anonymity}",callback=self.parse_proxyscrape,
                    meta={
                        "proxy":"185.30.232.18:9999"
                    }
                    )
        for socks4_country in socks4_country_code:
            yield scrapy.Request(url=f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country={socks4_country}",callback=self.parse_proxyscrape,
            meta={
                        "proxy":"185.30.232.18:9999"
            }
            )
        for socks5_country in socks5_country_code:
            yield scrapy.Request(url=f"https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country={socks5_country}",callback=self.parse_proxyscrape,)
    @_base
    def parse_sslproxies(self,response):
        for row in response.xpath("//table[@id='proxylisttable']/tbody/tr"):
            columns = row.css("td::text").getall()
            if len(columns) == 8:
                ip,port,code,country,anonymity,google,https,checked = columns
                yield {
                    "ip":ip,
                    "port":port,
                    "country_code":code,
                    "anonymity":anonymity.split()[0],
                    "protocol":"https" if https=="yes" else "http",
                    "last_checked":checked,
                }
    @_base
    def parse_spysme_txt(self,response):
        content = re.split("\n\n| \n\r\n",response.body.decode())[1]
        for proxy in content.split("\n"):
            proxy = re.split(" |-|:",proxy)
            if len(proxy)>3:
                yield {
                        "ip":proxy[0],
                        "port":proxy[1],
                        "country_code":proxy[2],
                        **dict.fromkeys(["anonymity","protocol","last_checked"],"unknown"),
                    }
    @_base
    def parse_proxyscrape(self,response):
        qs = parse_qs(urlparse(response.url).query)
        if qs.get("protocol")[0].startswith("http"):
            protocol,country_code,anonymity,ssl = [qs.get(param)[0] for param in ["protocol","country","anonymity","ssl"]]
        else:
            protocol,country_code = [qs.get(param)[0] for param in ["protocol","country"]]
            anonymity = "unknown"
        if protocol == "http":
            if ssl == "no":
                protocol = "http"
            else:
                protocol = "https"
        content = set(re.split("\n|\r",response.body.decode()))
        content.remove("")
        for proxy in content:
            proxy,port = proxy.split(":")
            yield {
                        "ip":proxy,
                        "port":port,
                        "country_code":country_code,
                        "anonymity":anonymity,
                        "protocol":protocol,
                        "last_checked":"unknown",
                    }