"""Shared prompt contracts for CLI-backed adapters."""


GENERATED_PROJECT_DEV_SERVER_CONTRACT = (
    "Nailaude generated-project dev-server contract: 如果你创建或修改 Vite、React、Next.js 或其他前端项目配置/脚本，"
    "不要设置 server.open、open: true 或任何会自动打开浏览器窗口的配置；"
    "不要硬编码 Nailaude 正在使用的端口（例如 5173、8000）或其他固定端口，除非用户明确要求。"
    "需要本地开发服务器时，让框架自动选择可用端口，或使用环境变量/命令行参数覆盖端口；"
    "不要运行会自动打开浏览器窗口的命令，验证优先使用类型检查、测试或生产构建。\n"
)


def generated_project_dev_server_contract(context: dict) -> str:
    """Return dev-server safety guidance for generated project tasks."""
    return GENERATED_PROJECT_DEV_SERVER_CONTRACT
