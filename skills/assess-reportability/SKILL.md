# assess-reportability

## 目的

根据 `collect result` 判断今天是否成立日报，以及是否需要直接进入 `blocked`。

## 输入

- `collect result`

## 判定规则

- 只要至少有一条有用内容，日报就成立
- `summary.useful_item_count >= 1` 时，允许继续进入 `build-report`
- `summary.useful_item_count == 0` 时，直接进入 `blocked`
- 部分 lane 异常不会自动阻断，只要仍有内容，就应继续产出日报

## 输出

最小输出应回答：

- `is_reportable`
- `reason_summary`
- `degraded_hint`

## 约束

- 这里只回答“能不能成立日报”
- 最终 `verdict` 仍由主链路后续步骤综合给出
