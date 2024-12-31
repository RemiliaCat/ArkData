from . import API
from . import assistant
from . import settings
from . import timer  # 来自简律纯提供的来自网络的定时任务模块
import OlivOS
import os
import re


class Event(object):
    def init(plugin_event, Proc: OlivOS.API.Proc_templet):
        if not os.path.exists(assistant.path()):
            os.mkdir(assistant.path())
        if not os.path.exists(assistant.path('src')):
            os.mkdir(assistant.path('src'))
        if not os.path.exists(assistant.path('src/gamedata/')):
            os.mkdir(assistant.path('src/gamedata/'))

        global strings
        strings = settings.Strings()
        global game_data
        game_data = API.Data()

        # 定时刷新数据
        Timer = timer.TaskTimer()
        Timer.join_task(refresh, [Proc], timing=4)
        Timer.start()

    def group_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        unity_reply(plugin_event, Proc, game_data)

    def private_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        print(strings.str_match_attrs)
        unity_reply(plugin_event, Proc, game_data)


def unity_reply(plugin_event: OlivOS.API.Event, Proc: OlivOS.API.Proc_templet, game_data: API.Data):
    # 变量初始化
    message = plugin_event.data.message
    item: API.Item = None
    stage: API.Data.Stage = None
    units_by_item = None
    list_format_args = {}

    # 匹配关键词
    match_result = re.match(
        strings.str_match_pattern, message, flags=re.I)

    # 关键词分支
    if match_result:
        match_attr = match_result.group('attr')
        match_name = match_result.group('name')

        # 掉率按素材
        if match_attr in strings.list_match_attr_item:
            # 变量设置
            item_name = match_name
            item_id = game_data.name_to_id(item_name)
            item = game_data.items[item_id]
            units_by_item = game_data.item_order(item.id)
            tip = ''

            # 材料验证
            if units_by_item == None:
                plugin_event.reply(strings.str_no_target)
                return

            # 筛选
            top = None
            max = None
            if len(units_by_item) >= 15:  # 如果有20个以上的单元，筛选最低理智期望的20个
                top = 15
            elif item.rarity == 0:
                max = 10
            elif item.rarity == 1:  # 否则，如果材料稀有等级为0~4，分别设置最小边界
                max = 20
            elif item.rarity == 2:
                max = 50
            elif item.rarity == 3:
                max = 100
            elif item.rarity == 4:
                max = None
            if top:
                units_by_item = assistant.selector(
                    units_by_item, top_rate=top)
                tip = '（已简化）'
            else:
                units_by_item = assistant.selector(
                    units_by_item, max_rate=min)
                tip = '（已简化）'

            # 字符串格式化并输出
            open_stages: str = ''
            for unit in units_by_item:
                unit: API.Data.MatrixUnit
                stage_code: str = game_data.id_to_name(
                    unit.stage_id, flag='stage')
                open_stages += stage_code + \
                    '(' + str(unit.ap_drop_rate) + '/' + \
                    str(round(unit.drop_probability*100, 1)) + '%)，'
            open_stages = open_stages[:-1]
            list_format_args = {'item_name': item_name,
                                'tip': tip, 'open_stages': open_stages}
            plugin_event.reply(
                strings.str_freply_item.format(**list_format_args))

        # 掉率按关卡
        elif match_attr in strings.list_match_attr_stage:
            # 变量设置
            stage_code = match_name
            stage_id = game_data.name_to_id(stage_code, flag='stage')
            units_by_stage = game_data.stage_order(stage_id)
            tip = ''

            # 关卡验证
            if units_by_stage == None:
                plugin_event.reply(strings.str_no_target)
                return

            # 筛选
            units_by_stage = assistant.selector(units_by_stage, is_open=True)

            # 字符串格式化并输出
            open_drop_items: str = ''
            for unit in units_by_stage:
                unit: API.Data.MatrixUnit
                tmp_item_name: str = game_data.id_to_name(
                    unit.item_id)
                open_drop_items += tmp_item_name + \
                    '(' + str(round(unit.drop_probability*100, 1)) + '%)，'
            open_drop_items = open_drop_items[:-1]
            list_format_args = {'stage_code': stage_code,
                                'tip': tip, 'open_drop_items': open_drop_items}
            plugin_event.reply(
                strings.str_freply_stage.format(**list_format_args))


def refresh(Proc: OlivOS.API.Proc_templet):
    game_data.get_and_refresh()
    Proc.log(1, '已刷新明日方舟游戏数据')