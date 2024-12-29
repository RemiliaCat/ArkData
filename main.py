from . import API
from . import assistant
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

        # try:
        #     global game_data
        #     game_data = API.Data()
        # except:
        #     Proc.log(2, '游戏数据加载失败')
        global game_data
        game_data = API.Data()

        # 定时刷新数据
        Timer = timer.TaskTimer()
        Timer.join_task(refresh, [Proc], timing=4)
        Timer.start()

    def group_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        unity_reply(plugin_event, Proc, game_data)

    def private_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        unity_reply(plugin_event, Proc, game_data)


def unity_reply(plugin_event: OlivOS.API.Event, Proc: OlivOS.API.Proc_templet, game_data: API.Data):
    # 变量初始化
    item: API.Item = None
    stage: API.Data.Stage = None
    units_by_item = None
    freply_item = '材料名称：{item_name}\n开放来源{tip}：\n（理智期望/掉率）\n{open_stages}\n数据来自企鹅物流数据统计（https://penguin-stats.io/）'
    freply_stage = '来源名称：{stage_code}\n材料掉率{tip}：\n\n{open_drop_items}\n数据来自企鹅物流数据统计（https://penguin-stats.io/）'
    list_format_args = {}
    message = plugin_event.data.message

    # 匹配关键词
    pattern_match1 = r'^[\./。!！](?P<attr>材料|掉率|材料掉率|材料掉率查询)\s*(?P<name>[^(?:材料|掉率|材料掉率|材料掉率查询)\s]+)\s*'
    result_match1 = re.match(pattern_match1, message, flags=re.I)
    pattern_match2 = r'^[\./。!！](?P<attr>关卡|关卡掉率|关卡掉率查询)\s*(?P<code>[^(?:关卡|关卡掉率|关卡掉率查询)\s]+)\s*'
    result_match2 = re.match(pattern_match2, message, flags=re.I)

    # 关键词分支
    if result_match1:
        # 变量设置
        item_name = result_match1.group('name')
        item_id = game_data.name_to_id(item_name)
        item = API.Item(game_data.items[item_id])
        units_by_item = game_data.item_order(item.id)
        tip = ''

        # 材料验证
        if units_by_item == None:
            plugin_event.reply('无匹配材料，请检查输入是否正确，如：大小写，符号')
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
        plugin_event.reply(freply_item.format(**list_format_args))

    elif result_match2:
        # 变量设置
        stage_code = result_match2.group('code')
        stage_id = game_data.name_to_id(stage_code, flag='stage')
        units_by_stage = game_data.stage_order(stage_id)
        tip = ''

        # 关卡验证
        if units_by_stage == None:
            plugin_event.reply('无匹配关卡，请检查输入是否正确，如：大小写，符号')
            return

        # 筛选
        units_by_stage = assistant.selector(units_by_stage, is_open=True)

        # 字符串格式化并输出
        open_drop_items: str = ''
        for unit in units_by_stage:
            tmp_item_name: str = game_data.id_to_name(
                unit.item_id)
            open_drop_items += tmp_item_name + \
                '(' + str(round(unit.drop_probability*100, 1)) + '%)，'
        open_drop_items = open_drop_items[:-1]
        list_format_args = {'stage_code': stage_code,
                            'tip': tip, 'open_drop_items': open_drop_items}
        plugin_event.reply(freply_stage.format(**list_format_args))


def refresh(Proc: OlivOS.API.Proc_templet):
    game_data.get_and_refresh()
    Proc.log(1, '已刷新明日方舟游戏数据')
