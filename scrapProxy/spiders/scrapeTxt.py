import asyncio,aiohttp,re
async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://spys.me/proxy.txt") as response:
            # while True:
            #     cont = await response.content
            #     if not cont:
            #         break
            content = await response.content.read(response.content.total_bytes)
            content = re.split("\n\n| \n\r\n",content.decode())[1]
            proxies = []
            for proxy in content.split("\n"):
                proxy = re.split(" |-|:",proxy)
                if len(proxy)>3:
                    proxies.append(
                        {
                            "ip":proxy[0],
                            "port":proxy[1],
                            "code":proxy[2],
                        }
                    )
            return proxies
if __name__ == "__main__":
    print(asyncio.run(main()))