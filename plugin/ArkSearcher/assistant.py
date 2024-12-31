import json


def path(pt: str = ''):
    '''
    参考amber-keter的功能函数写法
    '''
    return 'plugin/data/ArkData/' + pt


def write(pt: str, text: str):
    '''
    参考amber-keter的功能函数写法
    '''
    with open(pt, 'w', encoding='utf-8') as file:
        json.dump(text, file, indent=4, ensure_ascii=False)


def read(pt: str):
    '''
    参考amber-keter的功能函数写法
    返回一个dict或list对象
    '''
    with open(pt, 'r', encoding='utf-8') as file:
        return json.load(file)


def selector(units, is_open: bool = True, max_rate: float = None, top_rate: int = None):
    '''
    筛选器
    @info:  min_rate与top_rate二选一，优先top_rate
    @param: is_open:筛选已开放关卡/材料
    @param: max_rate:筛选最低理智期望
    @param: top_rate:筛选前n位最低理智期望
    '''
    is_min = True
    if top_rate:
        units = sorted(units, key=lambda x: x.ap_drop_rate)
        units = units[:top_rate]
        is_min = False
    for unit in units:
        if is_open:
            if unit.end is not None:
                units.remove(unit)
        if max_rate and is_min:
            if unit.ap_drop_rate > max_rate:
                units.remove(unit)
    return units
