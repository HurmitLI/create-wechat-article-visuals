# create-wechat-article-visuals

一个为中文微信公众号文章规划、生成和验收视觉素材的 Codex Skill。

它会先理解文章真正要表达的关系，再决定应该生成封面、流程图、架构图、对比图还是观点图。目标不是“给文章加几张好看的图”，而是让每张图都承担明确的信息表达任务。

## 能做什么

- 根据完整稿、提纲或选题制定配图计划
- 生成微信公众号横版封面
- 生成流程图、架构图、对比图、观点图和章节配图
- 为整篇文章建立统一的颜色、字体、线条和插画语言
- 为精确信息图保留 SVG 可编辑源文件，并导出 PNG 发布版
- 检查尺寸、比例、文件格式、文字准确性和手机端可读性
- 检查已有公众号图片并给出改进方案

默认会交付 1 张封面和 2–4 张正文图；如果文章只有少量视觉命题，它会主动减少图片，而不是为了凑数生成装饰图。

## 安装

将仓库克隆到 Codex 的个人 Skills 目录：

```bash
git clone https://github.com/HurmitLI/create-wechat-article-visuals.git ~/.codex/skills/create-wechat-article-visuals
```

安装后，可在 Codex 中通过 `$create-wechat-article-visuals` 显式调用。

## 使用示例

```text
$create-wechat-article-visuals 给这篇文章生成一张封面和三张正文配图
```

```text
$create-wechat-article-visuals 把这份文章中的多 Agent 工作流程画成公众号信息图
```

```text
$create-wechat-article-visuals 检查这些公众号配图的风格、比例和手机端可读性
```

也可以与公众号文章写作 Skill 一起使用：

```text
$write-tech-wechat-article 写一篇关于多 Agent 协作的文章，再用 $create-wechat-article-visuals 生成统一配图
```

## 工作方式

Skill 会按以下顺序执行：

1. 提取文章的核心判断。
2. 找出最值得可视化的过程、对比、层级、因果或系统结构。
3. 为每张图定义位置、结论、类型、元素、禁用元素、比例和文件名。
4. 统一整篇文章的视觉系统。
5. 根据内容选择生成式插画或精确 SVG 信息图。
6. 导出文件并进行尺寸、文字和移动端验收。

概念封面和人物场景适合使用图像生成能力；包含大量准确文字、系统关系或流程节点的图片优先使用 SVG，避免生成式图片中的伪文字和信息错误。

## 默认输出结构

```text
文章名_assets/
├── 00-公众号封面.png
├── 01-问题结构.png
├── 01-问题结构.svg
├── 02-方案对比.png
├── 02-方案对比.svg
└── 03-行动闭环.png
```

- 封面默认约为 `2.35:1`，建议宽度至少 1200 px。
- 正文图优先使用 `3:2` 或 `16:9`，建议宽度至少 1200 px。
- SVG 用于继续编辑，PNG 用于上传到微信公众号。

## 图片验收

仓库包含一个不依赖第三方库的基础验收脚本：

```bash
python3 scripts/audit_visuals.py \
  --cover path/to/00-cover.png \
  path/to/body-01.png \
  path/to/body-02.svg
```

脚本支持 PNG、JPEG 和 SVG，会检查：

- 图片能否读取
- 像素尺寸
- 封面与正文图比例
- 建议最小宽度
- 过大的文件体积

脚本检查不能代替人工视觉验收。最终仍需逐张确认中文标题、英文产品名、裁切、重叠、伪文字和缩小后的可读性。

## 默认视觉系统

科技深度稿默认使用克制的编辑插画风：

| 角色 | 颜色 | 用法 |
|---|---|---|
| 背景 | `#FAF8F4` | 暖白底色 |
| 正文 | `#2E2E31` | 标题、说明和主线 |
| 主色 | `#5C6FA3` | 系统节点和主要路径 |
| 强调 | `#C9633F` | 冲突、转折和唯一重点 |
| 辅助 | `#AAB5CE` | 次要路径、边框和注释 |

视觉规则并非固定模板。Skill 会根据文章气质调整，但会确保同一篇文章内部保持一致。

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── visual-system.md
└── scripts/
    └── audit_visuals.py
```

- `SKILL.md`：核心工作流和触发条件
- `agents/openai.yaml`：Codex 界面展示信息
- `references/visual-system.md`：详细视觉规范与 Prompt 结构
- `scripts/audit_visuals.py`：图片格式、尺寸和比例检查工具
