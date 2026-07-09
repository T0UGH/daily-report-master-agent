## HN 搜索

- **Kastra 给 Claude Code、Cursor 和 Codex 加运行时授权。** 它在 agent 工具调用执行前按确定性策略给出 allow/hold/deny，并可扫描本地会话历史，找出写入 secrets、触碰生产库、force push、curl-to-shell 等高风险动作。来源：[HN](https://news.ycombinator.com/item?id=48847526) / [Kastra](https://kastra.ai/)
- **Abralo 把多路 Claude Code 会话放进一个轻量桌面窗口。** 作者说 VS Code 扩展跑 3 个以上会崩，Abralo 用 Tauri 做并排监控、注意力提示和 5 小时/周额度告警；评论已有用户反馈会话进度刷新卡住。来源：[HN](https://news.ycombinator.com/item?id=48832797) / [Abralo](https://abralo.com/)
- **Spice 2.0 把“agent 可查询实时业务数据”做成无 ETL 分析节点。** 它从 Postgres、MySQL、MongoDB、DynamoDB 等做原生 CDC，称 3 亿行表约 9 分钟 bootstrap，并让 agent 在不压生产库的情况下查秒级新鲜数据。来源：[HN](https://news.ycombinator.com/item?id=48851086) / [Spice](https://spice.ai/blog/spice-2-0-is-now-available)
- **PandaPage 给 coding agent 一个临时发布 HTML 的 curl API。** 一次 POST 可上传 JSON 或 zip，页面默认 24 小时过期、用 KV TTL 和 R2 lifecycle 清理；适合让 Claude Code 直接把 mockup 或 demo 变成可分享 URL。来源：[HN](https://news.ycombinator.com/item?id=48842119) / [PandaPage](https://pandapage.clawshop.sh)
- **ByteAsk 做了面向 C/C++ 的 agent coding harness。** 它补上 gdb、clang-tidy、cppcheck、sanitizers、perf、benchmark、compile DB、Godbolt、符号化和反编译等工具，回应“Claude Code 不够贴合 C++ 工具链”的痛点。来源：[HN](https://news.ycombinator.com/item?id=48805309) / [ByteAsk](https://byteask.ai/)
