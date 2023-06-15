class config:
    # 自定义的关系
    relations = ["建筑师", "建筑商", "开发商", "结构工程师", "主承包商"]
    # 根据这个文件中的信息进行实体链接
    entire_buildings_info_path = "entire_buildings_info.json"
    # 存放建筑的信息，不包括关系对应的实体链接
    buildings_info_path = "buildings.json"
    # 存放实体和关系
    related_entities_path = "related_entities.json"
    # 存放从建筑物中抽取到的实体信息
    entities_from_analysis_path = "entity_from_analysis.json"
    # 存放实体的信息「buildings_info」和「entity_from_buildings」的并集
    entities_info_path = "entities_info.json"
