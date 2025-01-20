class Settings(object):
    '''
    带*号代表推荐设置
    '''

    def __init__(self):
        # 按素材时的格式串*
        self.str_freply_item = '材料名称：{item_name}\n开放来源{tip}：\n（理智期望/掉率）\n{open_stages}\n数据来自企鹅物流数据统计（https://penguin-stats.io/）'

        # 按关卡时的格式串*
        self.str_freply_stage = '来源名称：{stage_code}{tip}\n材料掉率：\n{open_drop_items}\n数据来自企鹅物流数据统计（https://penguin-stats.io/）'

        # 查询参数[掉率按素材]的设置*
        self.list_match_subcommand_item = ['掉率', '材料掉率',
                                           '材料掉率查询', '素材掉率', '素材掉率查询', 'itemdrop']

        # 查询参数[掉率按关卡]的设置*
        self.list_match_subcommand_stage = [
            '关卡', '关卡掉率', '关卡掉率查询', 'stagedrop']

        # 无目标回应*
        self.str_no_target = '无匹配目标，请检查输入是否正确，如：大小写，符号'

        # 正则表达化
        self.str_match_subcommand_item = ''
        for i in self.list_match_subcommand_item:
            self.str_match_subcommand_item = self.str_match_subcommand_item + i + '|'
        self.str_match_subcommand_item = self.str_match_subcommand_item[:-1]

        self.str_match_subcommand_stage = ''
        for i in self.list_match_subcommand_stage:
            self.str_match_subcommand_stage = self.str_match_subcommand_stage + i + '|'
        self.str_match_subcommand_stage = self.str_match_subcommand_stage[:-1]

        # 合并所有subcommand
        self.str_match_subcommands = self.str_match_subcommand_item + \
            '|'+self.str_match_subcommand_stage

        # 可自定义匹配命令
        # 请确保<subcommand>和<arg>存在
        # <subcommand>: 查询子命令
        # <arg>: 查询参数
        self.str_match_pattern = r'^[\./。!！]ark\s*(?P<subcommand>{})\s*(?P<arg>[^(?:{}\s]+)\s*'.format(
            self.str_match_subcommands,
            self.str_match_subcommands
        )

        # 数据刷新时间*
        self.int_refresh_timing = 4

        # get请求重试次数
        self.int_retry_get_times = 5
