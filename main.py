from spider import getTopN, extractInfo, extractBuildingsInfo
import json
from copy import deepcopy
from typing import List
from config import config


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
    entities_set = set()
    related_entities: List[RelatedEntity] = []
    for index, building in enumerate(buildings):
        print(
            "Processing Relations With %s..., %d / %d"
            % (building["entity"], index + 1, len(buildings))
        )
        entity1 = building["entity"]
        props = building["props"]
        for prop, value in props.items():
            if prop in config.relations:
                # 遍历该实体对应关系的所有实体链接
                if "links" not in value:
                    # ===> 处理文本中的\n和顿号
                    origin_text = value["text"]
                    split_text = origin_text.split("、")  # 使用第一个分隔符"、"拆分文本
                    final_text = []
                    for item in split_text:
                        final_text.extend(item.split("\n"))
                    # 处理文本中的\n和顿号 <===
                    for item in final_text:
                        # 如果该实体已经存在于集合中，则不再进行处理
                        if not entities_set.__contains__(item):
                            related_entities.append(RelatedEntity(entity1, item, prop))
                        res.append({"entity": item, "props": {}})
                    continue
                links = value["links"]
                for link in links:
                    if link["text"] in entities_set:
                        links.pop(index)
                entities = extractInfo(links)
                for entity in entities:
                    related_entities.append(
                        RelatedEntity(entity1, entity["entity"], prop)
                    )
                res.extend(entities)

    related_entities_json = [item.__dict__() for item in related_entities]
    writeToFile(related_entities_json, config.related_entities_path)
    writeToFile(res, config.entities_from_analysis_path)


# 获取从建筑物中抽取到的实体链接
def getLinks(buildings):
    for building in buildings:
        props = building["props"]
        for prop in props:
            if "links" in props[prop]:
                print([item["link"] for item in props[prop]["links"]])


# 获取排名前n的建筑物，并从维基百科上爬取信息，最终写入文件
def work(n):
    with open("buildings.txt", "r") as file:
        buildings_num = len(file.readlines())
    if n <= buildings_num:
        return

    buildings = getTopN(n)
    data = extractBuildingsInfo(buildings)
    with open(config.entire_buildings_info_path, "r") as file:
        exist_data = json.loads(file.read())
    data = exist_data + data
    writeToFile(data, config.entire_buildings_info_path)
    writeToFile(process(data), config.buildings_info_path)


# 合并两个文件中的实体信息
def merge_entities():
    with open(config.entities_from_analysis_path, "r") as file:
        entities_from_analysis = json.loads(file.read())
    with open(config.buildings_info_path, "r") as file:
        entities_from_buildings = json.loads(file.read())
    entities = entities_from_analysis + entities_from_buildings
    writeToFile(entities, config.entities_info_path)


# 获取当前已有建筑物实体的数量
def get_buildings_len():
    with open(config.buildings_info_path, "r") as file:
        entities = json.loads(file.read())
    print(len(entities))


# 获取实体的数量
def get_entities_len():
    with open(config.entities_info_path, "r") as file:
        entities = json.loads(file.read())
    print(len(entities))


# 获取存在关系的实体的数量
def get_related_entities_len():
    with open(config.related_entities_path, "r") as file:
        entities = json.loads(file.read())
    print(len(entities))


# main函数
if __name__ == "__main__":
    # work函数用于爬取指定数量的建筑物信息
    # work(100)
    # get_buildings_len()

    # analyze函数用于分析建筑物中含有的关系，并从维基百科中爬取该关系对应实体的信息
    # with open(config.entire_buildings_info_path, "r") as file:
    #     # buildings = json.loads(file.read())[35:]
    #     buildings = json.loads(file.read())

    # analyze(buildings)

    # merge_entities()

    # buildings_set = set([item["entity"] for item in buildings])
    # print(len(buildings_set))
    # print(len(buildings))

    # buildings_map = {}
    # 统计出哪个实体是重复的
    # for building in buildings:
    #     if buildings_map.__contains__(building["entity"]):
    #         buildings_map[building["entity"]] += 1
    #     else:
    #         buildings_map[building["entity"]] = 1
    # for key, value in buildings_map.items():
    #     if value > 1:
    #         print(key, value)

    # merge_entities函数用于合并两个文件中的实体信息
    # merge_entities()

    get_entities_len()
    get_related_entities_len()
