#!/usr/bin/env python3
"""AI Cost Tracker - Installation and setup."""
from setuptools import setup, find_packages

setup(
    name="ai-cost-tracker",
    version="1.0.0",
    description="Track and report LLM API usage and costs",
    author="OpenClaw",
    py_modules=[
        "tracker",
        "cli",
        "pricing",
        "openclaw_integration",
        "log_tool_call",
        "quick_log",
        "examples",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ai-cost=cli:main",
            "ai-cost-tracker=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
