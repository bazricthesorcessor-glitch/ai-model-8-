"""
Tools module - modular tool implementations for system actions.
Each tool: takes input → executes action → returns result.
"""

from .tool import Tool
from .schemas import ToolSchemas
from .registry import REGISTRY, ToolRegistry

# Import all tool implementations
from .browser import ClickElementTool, TypeTextTool, NavigateTool, ReadContentTool
from .keyboard import KeyboardTypeTool, HotKeyTool
from .mouse import MouseClickTool, MouseMoveTool, DragDropTool
from .vision import ScreenshotTool, FindElementTool, ReadTextTool
from .system import OpenAppTool, CloseAppTool, ExecuteCommandTool

# Import web tools
try:
    from .web import (
        WebSearchTool,
        FetchPageTool,
        ExtractTextTool,
        ExtractLinksTool,
        SemanticExtractTool,
        SearchAndExtractTool,
        ExtractArticleTool,
        ExtractProductTool,
        ExtractResearchTool,
        SummarizePageTool,
        BrowserNavigateTool,
        BrowserClickTool,
        BrowserTypeTool,
    )
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    WEB_TOOLS_AVAILABLE = False

__all__ = [
    "Tool",
    "ToolSchemas",
    "REGISTRY",
    "ToolRegistry",
    # Browser tools
    "ClickElementTool",
    "TypeTextTool",
    "NavigateTool",
    "ReadContentTool",
    # Keyboard tools
    "KeyboardTypeTool",
    "HotKeyTool",
    # Mouse tools
    "MouseClickTool",
    "MouseMoveTool",
    "DragDropTool",
    # Vision tools
    "ScreenshotTool",
    "FindElementTool",
    "ReadTextTool",
    # System tools
    "OpenAppTool",
    "CloseAppTool",
    "ExecuteCommandTool",
]

# Add web tools to exports if available
if WEB_TOOLS_AVAILABLE:
    __all__.extend([
        "WebSearchTool",
        "FetchPageTool",
        "ExtractTextTool",
        "ExtractLinksTool",
        "SemanticExtractTool",
        "SearchAndExtractTool",
        "ExtractArticleTool",
        "ExtractProductTool",
        "ExtractResearchTool",
        "SummarizePageTool",
        "BrowserNavigateTool",
        "BrowserClickTool",
        "BrowserTypeTool",
    ])


# ============================================================================
# INITIALIZE REGISTRY - Register all tools
# ============================================================================

# Browser tools
REGISTRY.register(ClickElementTool())
REGISTRY.register(TypeTextTool())
REGISTRY.register(NavigateTool())
REGISTRY.register(ReadContentTool())

# Keyboard tools
REGISTRY.register(KeyboardTypeTool())
REGISTRY.register(HotKeyTool())

# Mouse tools
REGISTRY.register(MouseClickTool())
REGISTRY.register(MouseMoveTool())
REGISTRY.register(DragDropTool())

# Vision tools
REGISTRY.register(ScreenshotTool())
REGISTRY.register(FindElementTool())
REGISTRY.register(ReadTextTool())

# System tools
REGISTRY.register(OpenAppTool())
REGISTRY.register(CloseAppTool())
REGISTRY.register(ExecuteCommandTool())

# Web tools (if available)
if WEB_TOOLS_AVAILABLE:
    REGISTRY.register(WebSearchTool())
    REGISTRY.register(FetchPageTool())
    REGISTRY.register(ExtractTextTool())
    REGISTRY.register(ExtractLinksTool())
    REGISTRY.register(SemanticExtractTool())
    REGISTRY.register(SearchAndExtractTool())
    REGISTRY.register(ExtractArticleTool())
    REGISTRY.register(ExtractProductTool())
    REGISTRY.register(ExtractResearchTool())
    REGISTRY.register(SummarizePageTool())
    REGISTRY.register(BrowserNavigateTool())
    REGISTRY.register(BrowserClickTool())
    REGISTRY.register(BrowserTypeTool())


# ============================================================================
# REGISTER TOOL SERVICE WITH ROUTER
# ============================================================================

from router import register_service
from .service import tool_service

register_service("tools", tool_service)
