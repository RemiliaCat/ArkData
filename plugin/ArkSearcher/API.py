from . import assistant
from . import settings
import requests


class Data(object):
    class MatrixUnit(object):
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
            self.ap_drop_rate: float = 0
            self.drop_probability: float = 0
            self.is_open: bool = False
            self.initUnit(unit)

        def initUnit(self, unit: dict):
            self.item_id: str = unit['itemId']
            self.stage_id: str = unit['stageId']
            self.zone_id: str = unit['zoneId']
            self.ap_cost: int = unit['apCost']
            self.open_time: int = unit['open_time']
            self.close_time: int = unit['close_time']
            self.start: int = unit['start']
            self.end: int = unit['end']
            self.times: int = unit['times']
            self.quantity: int = unit['quantity']
            self.ap_drop_rate: float = 0
            self.drop_probability: float = 0

            if self.close_time is None:
                self.is_open = True

            if self.times != 0:
                self.drop_probability = round((self.quantity / self.times), 3)
            if self.drop_probability != 0:
                self.ap_drop_rate = round(
                    (self.ap_cost / self.drop_probability), 1)

            tmp_zone = Data._get_zone(self.zone_id)
            self.zone_subtype = tmp_zone['subtype']

    class Item(object):
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

    class Stage(object):
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

    def __init__(self):
        self.matrix_url = 'https://penguin-stats.io/PenguinStats/api/v2/result/matrix?server=CN&show_closed_zones=true'
        self.items_url = 'https://penguin-stats.cn/PenguinStats/api/v2/items'
        self.stages_url = 'https://penguin-stats.cn/PenguinStats/api/v2/stages'
        self.zone_url = 'https://penguin-stats.io/PenguinStats/api/v2/zones/{}'
        self._matrix_response = None
        self._item_response = None
        self._stage_response = None
        self.matrix: list[self.MatrixUnit] = []
        self.items: dict[self.Item] = {}
        self.stages: dict[self.Stage] = {}
        self.zones: dict = {}
        self.get_and_refresh()

    def _get_zone(self, zone_id: str):
        tmp_response = requests.get(self.zone_url.format(zone_id))
        tmp_dict_zone = tmp_response.json()
        return tmp_dict_zone

    def _get_and_refresh_matrix(self):
        self._matrix_response = requests.get(self.matrix_url)
        if not self._matrix_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'resource/gamedata/matrix.json'), self._matrix_response.json())
        self._Matrix()
        return self._matrix_response

    def _get_and_refresh_item(self):
        self._item_response = requests.get(self.items_url)
        if not self._item_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'resource/gamedata/items.json'), self._item_response.json())
        self._Items()
        return self._item_response

    def _get_and_refresh_stage(self):
        self._stage_response = requests.get(self.stages_url)
        if not self._stage_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'resource/gamedata/stages.json'), self._stage_response.json())
        self._Stages()
        return self._stage_response

    def _Matrix(self):
        '''
        Drop Matrix Model
        {
            stageId: string,
            itemId: string,
            quantity: number,
            times: number,
            start: number,
            end: number
        }
        '''
        tmp_matrix: list = assistant.read(
            assistant.path('resource/gamedata/matrix.json'))['matrix']
        self.matrix = []
        for tmp_unit in tmp_matrix:
            tmp_stage = self.stages[tmp_unit['stageId']]
            tmp_unit['apCost'] = tmp_stage.ap_cost
            tmp_unit['zoneId'] = tmp_stage.zone_id
            tmp_unit['open_time'] = tmp_stage.existence.get('open_time')
            tmp_unit['close_time'] = tmp_stage.existence.get('close_time')
            tmp_MatrixUnit_unit = self.MatrixUnit(tmp_unit)
            self.matrix.append(tmp_MatrixUnit_unit)

        return self.matrix

    def _Items(self):
        '''
        items.json Model
        {
            "itemId": string,
            "name": string,
            "name_i18n": {
                dict
            },
            "existence": {
                "CN": {
                    "exist": bool
                },
                "JP": {
                    "exist": bool
                },
                "KR": {
                    "exist": bool
                },
                "US": {
                    "exist": bool
                }
            },
            "itemType": string,
            "sortId": int,
            "rarity": int,
            "groupID": string,
            "spriteCoord": [
                int
            ],
            "alias": {
                "ja": [
                    string
                ],
                "zh": [
                    string
                ]
            },
            "pron": {
                "ja": [
                    string
                ],
                "zh": [
                    string
                ]
            }
        },
        '''
        tmp_list_items: list = assistant.read(
            assistant.path('resource/gamedata/items.json'))
        self.items = {}
        if tmp_list_items is not None:
            for tmp_dict_item in tmp_list_items:
                tmp_Item_item = self.Item(tmp_dict_item)
                self.items[tmp_Item_item.id] = tmp_Item_item

        return self.items

    def _Stages(self):
        '''
        stages.json Model
        {
           "stageId": string,
           "zoneId": string,
           "stageType": string,
           "code": string,
           "code_i18n": {
              "en": string,
              "ja": string,
              "ko": string,
              "zh": string
           },
           "apCost": int,
           "existence": {
              "CN": {
                 "exist": bool
              },
              "JP": {
                 "exist": bool
              },
              "KR": {
                 "exist": bool
              },
              "US": {
                 "exist": bool
              }
           },
           "minClearTime": int,
           "dropInfos": [
              {
                 "dropType": string,
                 "bounds": {
                    "lower": int,
                    "upper": int
                 }
              }
           ]
        }
        '''
        tmp_list_stages: list = assistant.read(
            assistant.path('resource/gamedata/stages.json'))
        self.stages = {}
        if tmp_list_stages is not None:
            for tmp_dict_stage in tmp_list_stages:
                tmp_Stage_stage = self.Stage(tmp_dict_stage)
                self.stages[tmp_Stage_stage.id] = tmp_Stage_stage

        return self.stages

    def get_and_refresh(self):
        for i in range(5):
            if self._get_and_refresh_item() is not None:
                break
        for i in range(5):
            if self._get_and_refresh_stage() is not None:
                break
        for i in range(5):
            if self._get_and_refresh_matrix() is not None:
                break

    def name_to_id(self, name: str, flag: str = 'item'):
        if flag == 'item':
            tmp_items = assistant.item_filter(self.items)
            for key in tmp_items.keys():
                if name == self.items[key].name:
                    return self.items[key].id
        elif flag == 'stage':
            tmp_stages = assistant.stage_filter(self.stages)
            for key in tmp_stages.keys():
                if name == tmp_stages[key].code:
                    return tmp_stages[key].id

    def id_to_name(self, id: str, flag: str = 'item'):
        if flag == 'item':
            items = assistant.item_filter(self.items)
            if id in items.keys():
                return items[id].name
        elif flag == 'stage':
            stages = assistant.stage_filter(self.stages)
            if id in stages.keys():
                return stages[id].code

    def load_item(self, item_id) -> Item:
        return self.Item(self.items[item_id])

    def load_stage(self, stage_id) -> Stage:
        return self.Stage(self.stages[stage_id])

    def item_order(self, item_id) -> list[MatrixUnit]:
        # 参数检验
        if item_id == None:
            return

        list_result = []
        # item = self.load_item_data(item_id)
        for unit in self.matrix:
            if unit.item_id == item_id:
                list_result.append(unit)
        return list_result

    def stage_order(self, stage_id) -> list[MatrixUnit]:
        # 参数检验
        if stage_id == None:
            return

        list_result = []
        # stage = self.load_item_data(stage_id)
        for unit in self.matrix:
            if unit.stage_id == stage_id:
                list_result.append(unit)
        return list_result

    def item_and_stage_order(self, item_id, stage_id) -> dict:
        for unit in self.matrix:
            if unit.stage_id == stage_id and unit.item_id == item_id:
                return unit
