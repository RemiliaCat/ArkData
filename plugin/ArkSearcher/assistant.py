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


def matrix_filter(
    units, block_perm: bool = False,
    block_closure: bool = True,
    max_rate: float = None,
    top_rate: int = None
):
    '''Marix过滤器
    @info               :   min_rate与top_rate二选一，优先top_rate
    @param block_disperm:   筛选永久关卡（如CW-8·别传）
    @param block_closure:   筛选已开放关卡/物品
    @param max_rate     :   筛选最高理智期望
    @param top_rate     :   筛选前n位最低理智期望
    '''
    is_min = True
    if top_rate:
        units = sorted(units, key=lambda x: x.ap_drop_rate)
        units = units[:top_rate]
        is_min = False
    for unit in units:
        if block_perm:
            if unit.zone_subtype == 'ACTIVITY_PERMANENT':
                units.remove(unit)
        if block_closure:
            if unit.close_time is not None:
                units.remove(unit)
        if max_rate and is_min:
            if unit.ap_drop_rate > max_rate:
                units.remove(unit)
    return units


def item_filter(units: dict):
    '''items筛选器
    '''
    return units


def stage_filter(units: dict, block_perm: bool = True, block_closure: bool = True):
    '''stages过滤器
    '''
    for key in units.keys():
        if block_closure:
            if units[key].existence.get('close_time') is not None:
                units.pop(key)
        if block_perm:
            unit_id = units[key].id
            if unit_id[-5:-1] == '_perm':
                units.pop(key)
    return units
