## Hacker News

- **本地跑 SOTA LLM 的成本争议被拉到硬件与量化细节。** James O’Beirne 的 local-llm 指南在 HN 引发 103 条评论，用户提醒示例构建可能接近 5–5.5 万美元，4-bit/REAP 在长上下文编码和数据分析上会明显掉质量。 [HN](https://news.ycombinator.com/item?id=48775921) · [GitHub](https://github.com/jamesob/local-llm)

- **Wafer 用 AMD 跑 GLM-5.2 的性能/美元数据，引发“别只报 TPS”的讨论。** 评论希望补充 performance per watt 和量化精度；多人指出 FP4/低比特量化常让 Kimi、GLM 这类模型在真实任务中“看起来快、实际被削弱”。 [HN](https://news.ycombinator.com/item?id=48780417) · [文章](https://www.wafer.ai/blog/glm52-amd)

- **Mistral 发布 Leanstral 1.5，主打小模型做 Lean 证明与 bug finding。** HN 讨论认可“专用小模型低成本覆盖 OCR/文件分析/形式化任务”的价值，但也质疑对比基准偏旧、示例 bug 是否真是测试和 fuzzing 难覆盖的边界。 [HN](https://news.ycombinator.com/item?id=48780801) · [Mistral](https://mistral.ai/news/leanstral-1-5/)

- **SearXNG 热帖下，Searx 原作者转而推荐 Hister：本地全文索引可把浏览历史和文件内容经 MCP 给 AI 助手用。** 讨论也提醒 metasearch 仍依赖 Google 等后端，更多价值是绕开 AI Overview、广告和单一搜索入口。 [HN](https://news.ycombinator.com/item?id=48779454) · [SearXNG](https://github.com/searxng/searxng)

- **Dan Luu 的 agentic coding 笔记把 HN 讨论带到“大上下文世界模型”。** 评论认为百万级上下文让许多复杂提示工程被简化，但企业协作的新难点变成：如何让团队共同维护同一个业务世界模型，并自动发现约束过期。 [HN](https://news.ycombinator.com/item?id=48782671) · [文章](https://danluu.com/ai-coding/#appendix-agentic-loops-and-writing-this-post)

- **Kagi 给搜索产品加 AI toggle，同时因翻译成本调整服务。** 评论正面看待“想用时才出现 AI”的选择权，也有付费用户质疑 Kagi Translate 被临时移除、未来转订阅制是否削弱原订阅价值。 [HN](https://news.ycombinator.com/item?id=48779352) · [Changelog](https://kagi.com/changelog#10959)
