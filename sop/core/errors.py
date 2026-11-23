"""内核异常类型。

重试语义只依赖这里的类型：
- StepTimeout   : 超时类错误，引擎会按 retries 重试
- StepAssertion : 断言失败，永不重试
- StepFailure   : 其他确定性失败，永不重试
"""


class SopError(Exception):
    """所有 sop 自定义异常的基类。"""

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.detail = detail


class ConfigError(SopError):
    """环境配置加载 / 环境变量缺失。"""


class FlowError(SopError):
    """流程文件格式错误。"""


class TemplateError(SopError):
    """模板变量无法解析。"""


class LocatorTimeout(SopError):
    """定位描述中的候选策略在超时内都没有命中。"""


class LocatorInvalid(SopError):
    """CSS/XPath/frame 选择器语法非法，属于确定性错误。"""


class StepTimeout(SopError):
    """步骤超时，可重试。"""


class StepAssertion(SopError):
    """断言失败，不重试。"""


class StepAmbiguity(SopError):
    """定位命中多个元素且没有显式 first/index，不重试。"""


class StepFailure(SopError):
    """确定性步骤失败，不重试。"""
