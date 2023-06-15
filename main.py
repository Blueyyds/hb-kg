from spider import getTopN, extractInfo, extractBuildingsInfo
import json
from copy import deepcopy
from typing import List, Type


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


class RelatedEntity:
    def __init__(self, entity1, entity2, relation):
        self.entity1 = entity1
        self.entity2 = entity2
        self.relation = relation

    def __dict__(self):
        return {
            "entity1": self.entity1,
            "entity2": self.entity2,
            "relation": self.relation,
        }


# 分析建筑物中含有的关系，并从维基百科中爬取该关系对应实体的信息
def analyze(buildings):
    res = []
    related_entities: List[RelatedEntity] = []
    for index, building in enumerate(buildings):
        print(
            "Processing Relations With %s..., %d / %d"
            % (building["entity"], index + 1, len(buildings))
        )
        entity1 = building["entity"]
        props = building["props"]
        for prop, value in props.items():
            if prop in relations:
                # 遍历该实体对应关系的所有实体链接
                links = value["links"]
                entity = extractInfo(links)
                for item in entity:
                    related_entities.append(
                        RelatedEntity(entity1, item["entity"], prop)
                    )
                res.extend(entity)

    related_entities_json = [item.__dict__() for item in related_entities]
    writeToFile(related_entities_json, "related_entities.json")
    writeToFile(res, "test3.json")


# 获取从建筑物中抽取到的实体链接
def getLinks(buildings):
    for building in buildings:
        props = building["props"]
        for prop in props:
            if "links" in props[prop]:
                print([item["link"] for item in props[prop]["links"]])


# 获取排名前n的建筑物，并从维基百科上爬取信息，最终写入文件
def work(n):
    buildings = getTopN(n)
    data = extractBuildingsInfo(buildings)
    writeToFile(data, "test.json")
    writeToFile(process(data), "test2.json")


# main函数
if __name__ == "__main__":
    with open("test.json", "r") as file:
        buildings = json.loads(file.read())
    analyze(buildings)
    # work(5)
