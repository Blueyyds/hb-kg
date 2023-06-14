import requests
from bs4 import BeautifulSoup


# 定义一个通用的爬虫函数
def spider(key):
    url = "https://zh.wikipedia.org/wiki/" + key
    headers = {"Accept-Language": "zh-CN,zh;q=0.9"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


# 获取中国高度排名前n的摩天大楼
def getTopN(n):
    # 从buildings.txt中读取数据
    with open("buildings.txt", "r") as file:
        buildings = [str.strip(building) for building in file.readlines()]
    # 如果buildings.txt中的数据足够n个，则直接返回
    if len(buildings) >= n:
        return buildings[:n]
    # 如果buildings.txt中的数据不足n个，则从维基百科爬取数据
    soup = spider("中华人民共和国摩天大楼列表")
    table = soup.find("table", class_="wikitable sortable static-row-numbers")
    rows = table.find("tbody").find_all("tr")[1:]
    buildings = []
    for row in rows:
        if len(buildings) == n:
            break
        cells = row.find_all("td")
        cell = cells[0].contents[0]
        if cell.name == "a":
            building = cell.text.strip()
            buildings.append(building)
    print("Top %d buildings in China:\n" % n)
    print(buildings)
    # 把buildings写入文件中
    with open("buildings.txt", "w") as file:
        for building in buildings:
            file.write(building + "\n")
    return buildings


# 提取表格中的数据
def extraInfo(keys=[]):
    res = []
    for index, key in enumerate(keys):
        print("Processing %s..., %d / %d" % (key, index + 1, len(keys)))
        info = spider(key).find("table", class_="infobox")
        if info is None:
            continue
        data = {"entity": key, "props": {}}
        rows = info.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = cells[0].text.strip()
                if key == "坐标":
                    continue
                value = {"text": cells[1].text.strip()}
                if cells[1].findAll("a"):
                    links = [
                        {"text": a.text.strip(), "link": a.get("href")}
                        for a in cells[1].findAll("a")
                    ]
                    value["links"] = links

                data["props"][key] = value
        res.append(data)
    return res
