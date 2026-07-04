## HN 搜索

- **Ultracodex 用 Codex 跑 Claude Ultracode 工作流。** 作者想让 Claude Fable 负责规划/验证，把实现环节交给 Codex agents 执行同一批 JavaScript workflow scripts，用来节省 Claude 额度并实践“loop engineering”。来源：[HN](https://news.ycombinator.com/item?id=48776386) / [GitHub](https://github.com/YuanpingSong/ultracodex)
- **EEBench 用物理仿真评测 AI 电路设计。** 任务要求 agent 提交可编译的电路设计源码，grader 跑 compiler checks 和波形仿真；frontier 模型约 45–72%，Claude Fable 5 为 71.7%，开源模型在 5–13%。来源：[HN](https://news.ycombinator.com/item?id=48766320) / [EEBench](https://www.eebench.org/)
- **Emra 把“AI 生成应用”放进共享数据库工作区。** 它像 Notion meets Lovable：每个生成 app 共用一层数据库和服务层，后续可互相交互；评论直接追问它与 Lovable 的差异，核心看点是数据可下载与平台锁定边界。来源：[HN](https://news.ycombinator.com/item?id=48778145) / [Emra](https://emra.app)
- **Cadreen 预览 memory、governance、tool execution 一体化 agent 基础设施。** 现有 API、TypeScript/Python/Go SDK、CLI 和审计轨迹，目标是让 agent 记忆、决策、请求权限和执行工具都可治理。来源：[HN](https://news.ycombinator.com/item?id=48780219)
- **Imagent 给 agent workflow 加统一多媒体生成接口。** 它把图片、视频、语音生成包装成同一接口，评论首先问视频生成成本是否应由用户自带 API key 控制，说明多模态 agent 的成本归属仍是产品设计问题。来源：[HN](https://news.ycombinator.com/item?id=48770383) / [GitHub](https://github.com/unliftedq/imagent)
- **TermRover 把移动端 SSH/tmux 做成 coding-agent 操作台。** iOS/Android 原生终端围绕 tmux sessions/windows 做快捷操作，付费项包括 agent workflow 的无限图片附件和 voice mode；Mosh 尚未支持。来源：[HN](https://news.ycombinator.com/item?id=48723755) / [TermRover](https://termrover.sh/)
