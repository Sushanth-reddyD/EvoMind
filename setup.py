"""Setup script for EvoMind."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="evomind",
    version="0.1.0",
    description="Production-ready AI Agent System with dynamic tool creation and execution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="EvoMind Contributors",
    url="https://github.com/Sushanth-reddyD/EvoMind",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai agent llm tool-creation sandbox react tot reflexion",
    entry_points={
        "console_scripts": [
            "evomind=evomind.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
