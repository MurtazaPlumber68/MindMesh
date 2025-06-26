
"""
Setup script for RLLM CLI Assistant
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rllm-cli",
    version="0.1.0",
    author="RLLM Team",
    author_email="contact@rllm.dev",
    description="Real-Time LLM-Enhanced CLI Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rllm/rllm-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rllm=main:app",
        ],
    },
    extras_require={
        "openai": ["openai>=1.3.0"],
        "local": ["transformers>=4.35.0", "torch>=2.1.0"],
        "dev": ["pytest>=7.4.3", "pytest-asyncio>=0.21.1", "black>=23.11.0", "mypy>=1.7.1"],
    },
)
