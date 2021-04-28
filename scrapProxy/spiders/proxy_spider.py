import scrapy,re
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
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse_sslproxies)
        yield scrapy.Request(url="http://spys.me/proxy.txt",callback=self.parse_spysme_txt)
        yield scrapy.Request(url="https://api.proxyscrape.com/?request=getproxies&proxytype=all&country=all&ssl=all&anonymity=all",callback=self.parse_proxyscrape)
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
                    "anonymity":anonymity,
                    "https":https,
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
                        **dict.fromkeys(["anonymity","https","last_checked"],"unknown"),
                    }
    @_base
    def parse_proxyscrape(self,response):
        content = set(re.split("\n|\r",response.body.decode()))
        content.remove("")
        for proxy in content:
            proxy,port = proxy.split(":")
            yield {
                        "ip":proxy,
                        "port":port,
                        **dict.fromkeys(["country_code","anonymity","https","last_checked"],"unknown"),
                    }
