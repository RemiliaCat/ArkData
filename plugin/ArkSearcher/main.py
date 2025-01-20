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
        if not os.path.exists(assistant.path('resource')):
            os.mkdir(assistant.path('resource'))
        if not os.path.exists(assistant.path('resource/gamedata/')):
            os.mkdir(assistant.path('resource/gamedata/'))

        global obj_settings
        obj_settings = settings.Settings()
        global game_data
        game_data = API.Data(show_closed_zones=True)

        # 定时刷新数据
        Timer = timer.TaskTimer()
        # Timer.join_task(refresh, [Proc],
        #                 timing=obj_settings.int_refresh_timing)
        Timer.join_task(refresh, [Proc], timing=4)
        Timer.start()

    def group_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        unity_reply(plugin_event, Proc, game_data)

    def private_message(plugin_event, Proc: OlivOS.API.Proc_templet):
        unity_reply(plugin_event, Proc, game_data)


def unity_reply(plugin_event: OlivOS.API.Event, Proc: OlivOS.API.Proc_templet, game_data: API.Data):
    # 变量初始化
    message = plugin_event.data.message
    item: API.Item = None
    stage: API.Data.Stage_T = None
    units_by_item = None
    list_format_subcommands = {}

    # 匹配关键词
    match_result = re.match(
        obj_settings.str_match_pattern, message, flags=re.I)

    # 关键词分支
    if match_result:
        match_subcommand = match_result.group('subcommand')
        match_arg = match_result.group('arg')

        # 掉率按素材
        if match_subcommand in obj_settings.list_match_subcommand_item:
            # 变量设置
            item_name = match_arg
            item_id = game_data.name_to_id(item_name, flag='item')
            if item_id is list:
                if item_id.epmty():
                    plugin_event.reply(obj_settings.str_no_target)
                    return
                item_id = item_id[0]
            item = game_data.items[item_id]
            units_by_item = game_data.item_order(item.id)
            tip = ''

            # 材料验证
            if units_by_item == None:
                plugin_event.reply(obj_settings.str_no_target)
                return

            # 筛选
            top = None
            maxn = None
            # 如果有15个以上的单元，筛选最低理智期望的20个
            if len(units_by_item) >= 15:
                top = 15
            # 否则，如果材料稀有等级为0~4，分别设置最小边界
            elif item.rarity == 0:
                maxn = 10
            elif item.rarity == 1:
                maxn = 20
            elif item.rarity == 2:
                maxn = 50
            elif item.rarity == 3:
                maxn = 100
            elif item.rarity == 4:
                maxn = None
            if top:
                units_by_item = assistant.matrix_filter(
                    units_by_item, top_rate=top)
                tip = '（已简化）'
            else:
                units_by_item = assistant.matrix_filter(
                    units_by_item, max_rate=maxn)
                tip = '（已简化）'

            # 字符串格式化并输出
            open_stages: str = ''
            for unit in units_by_item:
                unit: API.Data.MatrixUnit_T
                stage_code: str = game_data.id_to_name(
                    unit['stage_id'], flag='stage')
                if '_rep' in unit['stage_id']:
                    stage_code += '·复刻'
                elif '_perm' in unit['stage_id']:
                    stage_code += '·永久'
                if stage_code is not None:
                    open_stages += stage_code + \
                        '(' + str(unit['ap_expec']) + '/' + \
                        str(round(unit['drop_prob']*100, 1)) + '%)，'
            open_stages = open_stages[:-1]
            list_format_subcommands = {'item_name': item_name,
                                       'tip': tip, 'open_stages': open_stages}
            plugin_event.reply(
                obj_settings.str_freply_item.format(**list_format_subcommands))

        # 掉率按关卡
        elif match_subcommand in obj_settings.list_match_subcommand_stage:
            # 变量设置
            stage_code = match_arg.replace('复刻', '').replace(
                '别传', '').replace('插曲', '')
            stage_id = game_data.name_to_id(stage_code, flag='stage')
            tip = ''

            if type(stage_id) == list:
                if stage_id.epmty():
                    plugin_event.reply(obj_settings.str_no_target)
                    return

                if '复刻' in match_arg:
                    stage_id = filter(
                        lambda x: '_rep' in x, stage_id)
                    tip = '·复刻'
                elif '插曲' in match_arg or '别传' in match_arg:
                    stage_id = filter(
                        lambda x: '_perm' in x, stage_id)
                    tip = '·永久'
                else:
                    stage_id = filter(
                        lambda x: not ('_perm' in x or '_rep' in x), stage_id)
                    tip = ''
                stage_id = list(stage_id).pop()
            units_by_stage = game_data.stage_order(stage_id)

            # 筛选
            if '别传' in stage_code:
                units_by_stage = game_data.stage_order(stage_id)
                units_by_stage = assistant.matrix_filter(
                    units_by_stage, show_perm_zone=True)
            elif '插曲' in stage_code:
                units_by_stage = assistant.matrix_filter(
                    units_by_stage, show_perm_zone=True)
            else:
                units_by_stage = assistant.matrix_filter(
                    units_by_stage, show_perm_zone=False)

            # 关卡验证
            if units_by_stage == None:
                plugin_event.reply(obj_settings.str_no_target)
                return

            # 字符串格式化并输出
            drop_items: str = ''
            for unit in units_by_stage:
                unit: API.Data.MatrixUnit_T
                tmp_item_name: str = game_data.id_to_name(
                    unit['item_id'], flag='item')
                drop_items += tmp_item_name + \
                    '(' + str(round(unit['drop_prob']*100, 1)) + '%)，'
            drop_items = drop_items[:-1]
            list_format_subcommands = {'stage_code': stage_code,
                                       'tip': tip, 'open_drop_items': drop_items}
            plugin_event.reply(
                obj_settings.str_freply_stage.format(**list_format_subcommands))


def refresh(Proc: OlivOS.API.Proc_templet):
    game_data.refresh()
    Proc.log('数据已刷新')
    print('数据已刷新')
