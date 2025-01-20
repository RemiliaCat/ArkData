import json
import requests


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


def get_response(url):
    for i in range(5):
        try:
            return requests.get(url)
        except:
            pass


def matrix_filter(
    units,
    show_perm_zone: bool = False,
    max_rate: float = None,
    top_rate: int = None
):
    '''Marix过滤器
    @info                   :   min_rate与top_rate二选一，优先top_rate
    @param show_perm_zone   :   筛选出永久关卡（如CW-8·别传）
    @param max_rate         :   筛选掉最高理智期望
    @param top_rate         :   筛选出前n位最低理智期望
    '''
    tmp_units = units
    if not show_perm_zone:
        for unit in tmp_units.copy():
            if unit['zone_subtype'] == 'ACTIVITY_PERMANENT':
                tmp_units.remove(unit)
    is_min = True
    if top_rate:
        is_min = False
        tmp_units = sorted(tmp_units, key=lambda x: x['ap_expec'])
        tmp_units = tmp_units[:top_rate]
    if max_rate and is_min:
        for unit in tmp_units.copy():
            if unit['ap_drop_rate'] > max_rate:
                tmp_units.remove(unit)
    return tmp_units


def item_filter(units: dict):
    '''items筛选器
    '''
    return units


def stage_filter(units: dict, stage_id: str = None, show_perm_zone: bool = False):
    '''stages过滤器
    '''
    tmp_units = units
    if stage_id is not None:
        if stage_id in units:
            tmp_units[stage_id] = units[stage_id]
        return tmp_units
    if not show_perm_zone:
        tmp_units = {key: value for key,
                     value in tmp_units.items() if not 'perm' in value.id}
    units = tmp_units
    return units


def zone_filter(units: dict):
    pass
