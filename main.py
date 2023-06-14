from spider import getTopN, extraInfo
import json
from copy import deepcopy


# 把爬取到的数据写入文件
def writeToFile(data, filename):
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    with open(filename, "w") as file:
        file.write(json_data)


# 把原先属性中带有链接的对象转换为文本
def process(data):
    simplify_data = deepcopy(data)
    if isinstance(data, list):
        for index, item in enumerate(data):
            props = item["props"]
            for prop in props:
                simplify_data[index]["props"][prop] = props[prop]["text"]
    return simplify_data


relations = ["建筑师", "开发商", "结构工程师", "主承包商"]


# 分析建筑物中含有的关系，并从维基百科中爬取该关系对应实体的信息
def analyze(buildings):
    for building in buildings:
        props = building["props"]
        if "建筑师" in props:
            set1 = set([])
            # for architect in props["建筑师"]:
            #     print(architect)
            #     architect = architect["text"]
            #     if architect not in buildings:
            #         print("Processing %s..." % architect)
            #         data = extraInfo([(architect, 1)])
            #         buildings.append(data[0])


# main函数
if __name__ == "__main__":
    # with open("test.json", "r") as file:
    #     buildings = json.loads(file.read())
    # analyze(buildings)
    # data = process(buildings)
    # writeToFile(data, "test2.json")
    # for building in buildings:
    #     print(building["props"]["建筑师"])
    with open("test.json", "r") as file:
        buildings = json.loads(file.read())

    data = process(buildings)
    writeToFile(data, "test2.json")
