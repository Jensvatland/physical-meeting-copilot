# Physical Meeting Copilot

**v0.1 预览版** — 面向线下面对面会议的开源、厂商无关运行时。

> **会议运行时负责听；用户的个人 AI 负责理解。**

[English README](README.md) · [当前状态](docs/STATUS.md) · [贡献指南](CONTRIBUTING.md) · [Mac 快速开始](docs/MAC.md)

## 这是什么

**Meeting Core** 负责采集会议室音频、维护结构化会议状态（转写、说话人、主张、调研、提醒），并通过 **MCP** 暴露给个人 AI（Hermes / OpenClaw 等），**不把助理/CRM/调研逻辑写进核心**。

**v0.1 使用模拟 ASR/分离说话人/翻译。** 麦克风到服务器通路可用，但还不会把真实普通话/英语说成文本。离线演示 `simulate_meeting` 是当前推荐的完整切片。

## 支持的语言（v0.1）

| 用途 | 语言 |
|------|------|
| 会议语音对 | **仅普通话（`zh-CN`）+ 英语（`en`）** |
| 项目文档 | 英文（权威）+ 本简体中文 README |
| 更多语言 | 欢迎后续以适配器形式贡献，不在 MVP 范围 |

## 快速开始

需要 Python 3.11+ 与 [uv](https://github.com/astral-sh/uv)。

```bash
git clone https://github.com/Jensvatland/physical-meeting-copilot.git
cd physical-meeting-copilot
chmod +x scripts/mac-smoke.sh
./scripts/mac-smoke.sh
```

无需麦克风、无需云 API Key。详见 [docs/MAC.md](docs/MAC.md)。

浏览器 UI（可选）：

```bash
export MEETING_CORE_DB=~/.physical-meeting-copilot/meetings.db
uv run meeting-gateway
# Chrome 打开 http://127.0.0.1:8787 — 勾选同意 — Start meeting
```

页面会标明 **Simulated ASR**，这是 v0.1 的预期行为。

## 如何贡献

我们特别欢迎：真实语音适配器（如 FunASR）、评测样本、文档与 UI 打磨（在真实 ASR 落地前请保留模拟提示）。

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [docs/STATUS.md](docs/STATUS.md)，并运行 `./scripts/mac-smoke.sh`。

## 许可

Apache-2.0 — 见 [LICENSE](LICENSE)。
