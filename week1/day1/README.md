# agent

最小异步 agent 程序。源码在 `agent/`，启动入口是根目录 `main.py`。

`agent_write/` 不是程序源码目录，它是 agent 通过工具读写文件的默认工作区。

运行：

```bash
conda run -n llamaindex python main.py
```

需要环境变量：

```bash
export DASHSCOPE_API_KEY="你的 key"
```

当前模型：

- 主 agent: `glm-5`
- tool_search_subagent: `qwen3.5-flash`

