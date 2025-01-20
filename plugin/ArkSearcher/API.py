from . import assistant
from . import settings
import requests
import time


class Data(object):

    def __init__(self, **kwargs):
        self.matrix_basic_url = 'https://penguin-stats.cn/PenguinStats/api/v2/result/matrix?'
        self.items_basic_url = 'https://penguin-stats.cn/PenguinStats/api/v2/items/'
        self.stages_basic_url = 'https://penguin-stats.cn/PenguinStats/api/v2/stages/'
        self.zone_basic_url = 'https://penguin-stats.cn/PenguinStats/api/v2/zones/'
        self.matrix: dict = {}
        self.matrix['by_item'] = {}
        self.matrix['by_stage'] = {}
        self.items: dict[self.Item_T] = {}
        self.stages: dict[self.Stage_T] = {}
        self.zones: dict = {}
        self.get_item_all()
        self.get_stage_all()
        self.get_zone_all()
        self.get_matrix(**kwargs)

    class MatrixUnit_T(object):
        def __init__(self, unit: dict):
            self.item_id: str = None
            self.stage_id: str = None
            self.zone_id: str = None
            self.zone_subtype: str = None
            self.ap_cost: int = -1
            self.open_time: int = None
            self.close_time: int = None
            self.start: int = None
            self.end: int = None
            self.times: int = None
            self.quantity: int = None
            self.ap_expec: float = 0
            self.drop_prob: float = 0
            self.is_open: bool = False
            self.initUnit(unit)

        def initUnit(self, unit: dict):
            self.item_id: str = unit['itemId']
            self.stage_id: str = unit['stageId']
            self.zone_id: str = unit['zoneId']
            self.zone_subtype = None
            self.ap_cost: int = unit['apCost']
            self.open_time: int = unit['open_time']
            self.close_time: int = unit['close_time']
            self.start: int = unit['start']
            self.end: int = unit['end']
            self.times: int = unit['times']
            self.quantity: int = unit['quantity']
            self.ap_expec: float = 0
            self.drop_prob: float = 0
            self.get_subType()

            if self.close_time is None:
                self.is_open = True

            if self.times != 0:
                self.drop_prob = round((self.quantity / self.times), 3)
            if self.drop_prob != 0:
                self.ap_expec = round(
                    (self.ap_cost / self.drop_prob), 1)

        def is_close(self):
            if self.close_time is None:
                return False
            # time.time():s，close_time:ms
            return time.time() * 1000 > self.close_time

        def get_subType(self):
            self.zone_subtype = None
            tmp_zone_response = requests.get(
                'https://penguin-stats.cn/PenguinStats/api/v2/zones/{}'.format(self.zone_id))
            if not tmp_zone_response == 200:
                tmp_zone = tmp_zone_response.json()
                self.zone_subtype = tmp_zone['subType']
            return self.zone_subtype

    class Item_T(object):
        '''
        暂不清楚为什么要用Item类代替Item字典
        '''

        def __init__(self, item: dict):
            self.id: str = ''
            self.icon_id: str = ''
            self.name: str = ''
            self.rarity: int = -1
            self.initItem(item)

        def initItem(self, item: dict):
            if 'itemId' in item:
                self.id: str = item['itemId']
            if 'iconId' in item:
                self.icon_id: str = item['iconId']
            if 'name' in item:
                self.name: str = item['name']
            if 'rarity' in item:
                self.rarity: int = item['rarity']

    class Stage_T(object):
        '''
        暂不清楚为什么要用Stage类代替Stage字典
        '''

        def __init__(self, stage: dict):
            self.id: str = ''
            self.code: str = ''
            self.zone_id: str = ''
            self.ap_cost: int = -1
            self.existence: dict = {}
            self.initStage(stage)

        def initStage(self, stage: dict):
            self.id: str = stage['stageId']
            self.code: str = stage['code']
            self.zone_id: str = stage['zoneId']
            self.ap_cost: int = stage['apCost']
            self.existence: dict = stage['existence']['CN']

    # def __get_zone(self, zone_id):
    #     tmp_response = requests.get(self.zone_basic_url+zone_id)
    #     if not tmp_response.status_code == 200:
    #         return None
    #     tmp_dict_zone = tmp_response.json()
    #     return tmp_dict_zone

    def refresh(self):
        self.get_item_all()
        self.get_stage_all()
        self.get_zone_all()
        self.get_matrix()

    def get_matrix(self, **kwargs):
        tmp_matrix_url = self.matrix_basic_url
        if kwargs != {}:
            for key, value in kwargs.items():
                tmp_matrix_url += '{}={}&'.format(key, value)
            tmp_matrix_url = tmp_matrix_url[:-1]
        tmp_matrix_response = assistant.get_response(tmp_matrix_url)
        if not tmp_matrix_response.status_code == 200:
            return None

        self.matrix['by_item'].clear()
        self.matrix['by_stage'].clear()
        tmp_list_matrix = tmp_matrix_response.json()['matrix']
        # tmp_matrix = self.Matrix_T()
        tmp_matrix = self.matrix
        assistant.write(assistant.path(
            'resource/gamedata/matrix.json'), tmp_matrix_response.json())
        for tmp_raw_unit in tmp_list_matrix:
            tmp_new_unit = {}
            tmp_stage = self.stages[tmp_raw_unit['stageId']]
            tmp_new_unit['item_id'] = tmp_raw_unit['itemId']
            tmp_new_unit['stage_id'] = tmp_raw_unit['stageId']
            tmp_new_unit['zone_id'] = tmp_stage.zone_id
            tmp_new_unit['zone_subtype'] = self.zones[tmp_stage.zone_id]['subType']
            tmp_new_unit['ap_cost'] = tmp_stage.ap_cost
            tmp_new_unit['quantity'] = tmp_raw_unit['quantity']
            tmp_new_unit['times'] = tmp_raw_unit['times']
            tmp_new_unit['open_time'] = tmp_stage.existence.get('open_time')
            tmp_new_unit['close_time'] = tmp_stage.existence.get('close_time')
            tmp_new_unit['drop_prob'] = self.__calcu_drop_prob(
                tmp_new_unit['quantity'], tmp_new_unit['times'])
            tmp_new_unit['ap_expec'] = self.__calcu_ap_expec(
                tmp_new_unit['ap_cost'], tmp_new_unit['drop_prob'])
            if not tmp_new_unit['item_id'] in tmp_matrix['by_item']:
                tmp_matrix['by_item'][tmp_new_unit['item_id']] = []
            if not tmp_new_unit['stage_id'] in tmp_matrix['by_stage']:
                tmp_matrix['by_stage'][tmp_new_unit['stage_id']] = []
            tmp_matrix['by_item'][tmp_new_unit['item_id']].append(tmp_new_unit)
            tmp_matrix['by_stage'][tmp_new_unit['stage_id']].append(
                tmp_new_unit)
        self.matrix = tmp_matrix

    def get_item_single(self, item_id):
        tmp_item_response = requests.get(
            self.items_basic_url + item_id)
        if not tmp_item_response.status_code == 200:
            return None
        tmp_dict_item = tmp_item_response.json()
        tmp_object_item = self.Item_T(tmp_dict_item)
        self.items[tmp_object_item.id] = tmp_object_item
        return tmp_object_item

    def get_item_all(self):
        tmp_item_response = assistant.get_response(self.items_basic_url)
        if not tmp_item_response.status_code == 200:
            return None

        self.items.clear()
        tmp_list_items = tmp_item_response.json()
        assistant.write(assistant.path(
            'resource/gamedata/items.json'), tmp_list_items)
        if tmp_list_items is not None:
            for tmp_dict_item in tmp_list_items:
                tmp_object_item = self.Item_T(tmp_dict_item)
                self.items[tmp_object_item.id] = tmp_object_item
        return self.items

    def get_stage_single(self, stage_id):
        tmp_stage_response = requests.get(
            self.items_basic_url + stage_id)
        if not tmp_stage_response.status_code == 200:
            return None
        tmp_dict_stage = tmp_stage_response.json()
        tmp_object_stage = self.Stage_T(tmp_dict_stage)
        return tmp_object_stage

    def get_stage_all(self):
        tmp_stage_response = requests.get(self.stages_basic_url)
        if not tmp_stage_response.status_code == 200:
            return None

        tmp_list_stages = tmp_stage_response.json()
        self.stages = {}
        assistant.write(assistant.path(
            'resource/gamedata/stages.json'), tmp_list_stages)
        if tmp_list_stages is not None:
            for tmp_dict_stage in tmp_list_stages:
                tmp_object_stage = self.Stage_T(tmp_dict_stage)
                self.stages[tmp_object_stage.id] = tmp_object_stage
        return self.stages

    def __calcu_drop_prob(self, quantity, times):
        if times == 0 or quantity == 0:
            return 0
        return round((quantity / times), 3)

    def __calcu_ap_expec(self, ap_cost, drop_prob):
        if drop_prob == 0:
            return 2e31
        return round((ap_cost / drop_prob), 1)

    def get_zone_all(self):
        tmp_zone_response = assistant.get_response(
            self.zone_basic_url)
        if not tmp_zone_response.status_code == 200:
            return None

        self.zones.clear()
        tmp_list_zones = tmp_zone_response.json()
        for tmp_dict_zone in tmp_list_zones:
            self.zones[tmp_dict_zone['zoneId']] = tmp_dict_zone
        return self.zones

    # return: str | list[str]
    def name_to_id(self, name: str, flag: str):
        # 为了防止重名物品/关卡，返回所有匹配的物品/关卡id,但理论上不存在重名物品
        list_res = []
        if flag == 'item':
            for key in self.items.keys():
                if name == self.items[key].name:
                    list_res.append(self.items[key].id)
        elif flag == 'stage':
            for key in self.stages.keys():
                if name == self.stages[key].code:
                    list_res.append(self.stages[key].id)
                    # 目前只可能存在初始、复刻、别传/插曲关卡
                    if list_res.__len__() >= 3:
                        return list_res
        # 如果只有一个匹配项，返回该项
        if list_res.__len__() == 1:
            return list_res[0]
        else:
            return list_res

    def id_to_name(self, id: str, flag: str):
        if flag == 'item':
            if id in self.items.keys():
                return self.items[id].name
        elif flag == 'stage':
            if id in self.stages.keys():
                return self.stages[id].code

    def item_order(self, item_id) -> list:
        return self.matrix['by_item'][item_id]

    def stage_order(self, stage_id) -> list:
        return self.matrix['by_stage'][stage_id]

    def item_and_stage_order(self, item_id, stage_id) -> MatrixUnit_T:
        for unit in self.matrix['by_item'][item_id]:
            if unit['stageId'] == stage_id:
                return self.MatrixUnit_T(unit)

    def set_args(self, **kwargs):
        self.get_matrix(kwargs)
