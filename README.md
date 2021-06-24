# auto-derby

[![python](https://github.com/NateScarlet/auto-derby/actions/workflows/python-app.yml/badge.svg)](https://github.com/NateScarlet/auto-derby/actions/workflows/python-app.yml)

自动化养马

[育成结果 Nurturing result](https://github.com/NateScarlet/auto-derby/wiki/Nurturing-result)

## 功能

- [x] 支持客户端
  - [x] DMM （前台）
  - [x] _实验性_ 安卓 ADB 连接（后台）开发基于 1080x1920 分辨率
- [x] 团队赛 (Team race)
  - [x] 有胜利确定奖励时吃帕菲
- [x] 日常赛 (Daily race)
- [x] PvP 活动赛 (Champions meeting)
- [x] 传奇赛 (Legend race)
  - [x] 自动领奖励
- [x] 活动抽奖转盘 (Roulette derby)
- [x] 遇到限时商店自动买空
- [x] 育成 (Nurturing)
  - [x] 自动选择训练
    - [x] 基于当前属性
    - [x] 基于训练效果
    - [x] 基于训练等级
    - [ ] 基于精确体力消耗
    - [ ] 基于羁绊值获取量
    - [x] 暑期集训保留体力
    - [ ] 年末抽奖前消耗体力
  - [x] 遇到新事件选项请求人工处理，后续相同事件使用相同选择
  - [x] 自动参加比赛
    - [x] 预估比赛结果，如果不能仅靠属性拿冠军则暂停请求人工确认
    - [x] 自动选择比赛跑法
      - [x] 基于属性和适性
      - [ ] 基于对手跑法选择跑法（倾向人数少的跑法）
  - [ ] 支持友人卡（在实现前可以带友人卡，就是外出时需要自己手动选）
- [x] 支持 python 插件

## 使用方法

需求 DMM 版 和 python3.8

安装依赖

```shell
py -3.8 -m pip install -r requirements.txt
```

双击 `launcher.cmd` 可通过一个简单的 GUI 进行启动

或者手动调用模块：

```shell
py -3.8 -m auto_derby 工作名称
```

工作名称随便输入错误的名字会提示当前支持的工作

## 问题反馈

通过 [Github issues](https://github.com/NateScarlet/auto-derby/issues) 提交反馈

启动器勾选 debug 时会在同目录下生成相关调试信息，反馈时请将相关信息一同附上

## launcher.log

启动器日志，强制退出时不会包含运行日志

反馈前请手动清理敏感信息（例如用户名、机器名）

## auto_derby.log

运行日志，`.1` `.2` `.3` 后缀的文件为之前日志的备份

## last_screenshot.local.png

脚本的最后一次截图

## ocr_images.local

文本识别时使用的图片

## single_mode_event_images.local

育成事件选择时用于匹配的图片
