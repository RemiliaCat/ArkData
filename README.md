# ArkData
> **ArkData for OlivOS**，这是一个明日方舟数据相关的 [OlivOS](https://github.com/OlivOS-Team/OlivOS) 插件与 [OlivaDice](https://github.com/OlivOS-Team/OlivaDiceCore) 扩展文件的仓库

## ArkSearcher Plugin
> **ArkSearcher** 提供以`/ark`开头、通过不同的`Command`实现不同的功能的 OlivOS 机器人指令，用于查询明日方舟游戏数据。

### Command

#### Command Table
| Command | Argument     | Parameter     | Usage                   |
|---------|--------------|---------------|-------------------------|
| item    | <item_name>  | [素材名称]    | 按素材名查询掉率        |
| stage   | <stage_code> | [关卡/物品名] | 按关卡名/物品名查询掉率 |

#### Example
```python
/ark stage 1-7  -> 查询关卡1-7的素材掉率
```

## ArkData Extends
> **ArkData Extends** 提供明日方舟数据相关的 OlivaDice 的deck及mod扩展文件
### Tips
> 请将本仓库`extend/arkimages/`置于 OlivOS 的`data/images/`下

## 声明
> 本仓库部分数据由 [企鹅物流数据统计](https://penguin-stats.io/) 提供。使用的一切数据，版权均归属 [Arknights/上海鹰角网络科技有限公司](https://www.hypergryph.com/) ，仅用于学习和交流。