from . import assistant
import requests


class Data(object):
    class MatrixUnit(object):
        def __init__(self, unit: dict):
            self.item_id: str = unit['itemId']
            self.stage_id: str = unit['stageId']
            self.ap_cost: int = unit['apCost']
            self.times: int = unit['times']
            self.quantity: int = unit['quantity']
            self.ap_drop_rate: float = 0
            self.drop_probability: float = 0
            if self.times != 0:
                self.drop_probability = round((self.quantity / self.times), 3)
            if self.drop_probability != 0:
                self.ap_drop_rate = round(
                    (self.ap_cost / self.drop_probability), 1)
            self.start: int = unit['start']
            self.end: int = unit['end']
            self.is_open: bool = None
            if self.end == None:
                self.is_open = True
            else:
                self.is_open = False

    class Item(object):
        '''
        暂不清楚为什么要用Item类代替Item字典
        '''

        def __init__(self, item: dict):
            self.id: str = item['itemId']
            self.name: str = item['name']
            self.rarity: int = item['rarity']
            self.group_id: str = item['groupID']

    class Stage(object):
        '''
        暂不清楚为什么要用Stage类代替Stage字典
        '''

        def __init__(self, stage: dict):
            self.id: str = stage['stageId']
            self.code: str = stage['code']
            self.ap_cost: int = stage['apCost']

    def __init__(self):
        self.matrix_url = 'https://penguin-stats.cn/PenguinStats/api/v2/result/matrix'
        self.item_url = 'https://penguin-stats.cn/PenguinStats/api/v2/items'
        self.stage_url = 'https://penguin-stats.cn/PenguinStats/api/v2/stages'
        self.matrix_response = None
        self.item_response = None
        self.stage_response = None
        self.matrix: list[self.MatrixUnit] = []
        self.items: dict[self.Item] = {}
        self.stages: dict[self.Stage] = {}
        self.get_and_refresh()

    def _get_and_refresh_matrix(self):
        self.matrix_response = requests.get(self.matrix_url)
        if not self.matrix_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'src/gamedata/matrix.json'), self.matrix_response.json())
        self._Matrix()
        return self.matrix_response

    def _get_and_refresh_item(self):
        self.item_response = requests.get(self.item_url)
        if not self.item_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'src/gamedata/items.json'), self.item_response.json())
        self._Items()
        return self.item_response

    def _get_and_refresh_stage(self):
        self.stage_response = requests.get(self.stage_url)
        if not self.stage_response.status_code == 200:
            return None
        assistant.write(assistant.path(
            'src/gamedata/stages.json'), self.stage_response.json())
        self._Stages()
        return self.stage_response

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
            assistant.path('src/gamedata/matrix.json'))['matrix']
        self.matrix = []
        for tmp_dict_unit in tmp_matrix:
            tmp_dict_unit['apCost'] = self.stages[tmp_dict_unit['stageId']].ap_cost
            tmp_MatrixUnit_unit = self.MatrixUnit(tmp_dict_unit)
            self.matrix.append(tmp_MatrixUnit_unit)

        return self.matrix

    def _Items(self):
        '''
           items.json Model
           {
              "itemId": string,
              "name": string,
              "name_i18n": {
                 "en": string,
                 "ja": string,
                 "ko": string,
                 "zh": string
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
                 int,
                 int
              ],
              "alias": {
                 "ja": [
                       "入門作戦記録",
                       "にゅうもんさくせんきろく",
                       "ニュウモンサクセンキロク"
                 ],
                 "zh": [
                       "基础作战记录",
                       "狗粮",
                       "录像带",
                       "经验卡"
                 ]
              },
              "pron": {
                 "ja": [
                       "nyuumon`sakusen`kiroku",
                       "nyuumon`sakusen`kiroku"
                 ],
                 "zh": [
                       "ji`chu`zuo`zhan`ji`lu",
                       "gou`liang",
                       "lu`xiang`dai",
                       "jing`yan`ka"
                 ]
              }
           },
           '''
        tmp_list_items: list = assistant.read(
            assistant.path('src/gamedata/items.json'))
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
            assistant.path('src/gamedata/stages.json'))
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
            for i in self.items.keys():
                if name == self.items[i].name:
                    return i
        elif flag == 'stage':
            for i in self.stages.keys():
                if name == self.stages[i].code:
                    return i

    def id_to_name(self, id: str, flag: str = 'item'):
        if flag == 'item':
            if id in self.items.keys():
                return self.items[id].name
        elif flag == 'stage':
            if id in self.stages.keys():
                return self.stages[id].code

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
