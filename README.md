# auto-derby

[![python](https://github.com/NateScarlet/auto-derby/actions/workflows/python-app.yml/badge.svg)](https://github.com/NateScarlet/auto-derby/actions/workflows/python-app.yml)

自动化养马

2021-06-14: 重炮 3 速 2 智 1 体 自动养成结果为 8250 分 URA 冠军，20 战 17 胜 312500 粉丝，比赛前手动学技能，无手动参赛。

2021-06-01: 气槽 3 速 2 智 1 体 自动养成结果为 10300 分 URA 冠军，历代评价点第一，无手动干预

2021-05-31: 麦昆 3 速 2 智 1 体 自动养成结果为 9100 分 URA 冠军，第一年手动出战一次

2021-05-30: 气槽 3 速 2 智 1 体 自动养成结果为 9800 分 URA 冠军，历代评价点第二，无手动干预

2021-05-30: 大和赤骥 3 速 2 智 1 体 自动养成结果为 9300 分 URA 冠军，第一年手动出战一次

## 功能

- [x] 团队赛 (Team race)
  - [x] 有胜利确定奖励时吃帕菲
- [x] 日常赛 (Daily race)
- [x] 传奇赛 (Legend race)
  - [x] 自动领奖励
- [x] 活动抽奖转盘 (Roulette derby)
- [x] 遇到限时商店自动买空
- [x] 育成 (Nurturing)
  - [x] 根据当前属性选择训练
  - [x] 遇到新事件选项请求人工处理，后续相同事件使用相同选择
  - [x] 根据训练效果选择训练
  - [x] 给暑期集训保留体力
  - [x] 自动参加比赛
  - [x] 预估比赛结果，如果不能仅靠属性拿冠军则暂停请求人工确认
  - [x] 根据属性和适性自动选择比赛跑法（非长距离或者低等级赛事倾向逃）
  - [ ] 支持友人卡（在实现前可以带友人卡，就是外出时需要自己手动选）

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
