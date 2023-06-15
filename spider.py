import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import re


# 定义一个通用的爬虫函数
def spider(url):
    headers = {"Accept-Language": "zh-CN,zh;q=0.9"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查响应状态码，若不是200会抛出异常
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        print("网络请求异常:", e)
        return None


# 获取中国高度排名前n的摩天大楼
def getTopN(n):
    # 从buildings.txt中读取数据
    with open("buildings.txt", "r") as file:
        buildings = [str.strip(building) for building in file.readlines()]
    # 如果buildings.txt中的数据足够n个，则直接返回
    if len(buildings) >= n:
        return buildings[:n]
    # 如果buildings.txt中的数据不足n个，则从维基百科爬取数据
    soup = spider("https://zh.wikipedia.org/wiki/中华人民共和国摩天大楼列表")
    table = soup.find("table", class_="wikitable sortable static-row-numbers")
    rows = table.find("tbody").find_all("tr")[len(buildings) + 1 : n + 1]
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
    # 把buildings写入文件中
    with open("buildings.txt", "a") as file:
        for building in buildings:
            file.write(building + "\n")
    return buildings


# 判断参数link是什么类型的链接
def judgeLink(link):
    # 如果link是字典，说明是带有文本的链接
    link = link["link"] if isinstance(link, dict) else link
    if link.startswith("https://"):  # 1. https链接
        return 1
    elif link.startswith("/wiki/"):  # 2. /wiki/开头的链接
        return 2
    else:  # 3. 非常规链接
        return 3


# 提取建筑物的信息，属性中包含链接
def extractBuildingsInfo(keys=[]):
    res = []
    for index, key in enumerate(keys):
        url = "https://zh.wikipedia.org/wiki/" + key
        print("Processing %s..., %d / %d" % (key, index + 1, len(keys)))
        info = spider(url)
        if info is None:
            continue
        info = info.find("table", class_="infobox")
        if info is None:
            print("Error: No infobox found in %s" % key)
            continue
        data = {"entity": key, "props": {}}
        rows = info.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = cells[0].get_text("\n").strip()
                if key == "坐标":  # 去除坐标信息
                    continue
                # 1. 去除文本中的锚点链接 2. 保留文本的换行符
                text = re.sub(r"\[\d+\]", "", cells[1].get_text("\n").strip())
                value = {"text": text}
                if cells[1].findAll("a"):
                    # 使用unquote函数对链接进行解码
                    links = [
                        {"text": a.text.strip(), "link": unquote((a.get("href")))}
                        for a in cells[1].findAll("a")
                        if a.text.strip() != ""
                        and not re.match(r"^\[\d+\]$", a.text.strip())  # 去除类似[1]这样的链接
                    ]
                    value["links"] = links

                data["props"][key] = value
        res.append(data)
    return res


# 提取表格中的数据
def extractInfo(links=[]):
    res = []
    for index, link in enumerate(links):
        if judgeLink(link) == 1:  # https链接
            entity_name = link["text"]
            url = link["link"]
        elif judgeLink(link) == 2:  # /wiki/开头的链接
            entity_name = link["text"]
            url = "https://zh.wikipedia.org" + link["link"]
        else:  # 非常规链接
            continue
        print("Processing %s..., %d / %d" % (entity_name, index + 1, len(links)))
        info = spider(url)
        if info is None:
            continue
        info = info.find("table", class_="infobox")
        if info is None:
            continue
        data = {"entity": entity_name, "props": {}}
        rows = info.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) == 2:
                key = cells[0].text.strip()  # 属性值
                value = re.sub(r"\[\d+\]", "", cells[1].text.strip())  # 去除文本中的锚点链接
                data["props"][key] = value
        res.append(data)
    return res
