from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

try:
    with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
        long_description = "\n" + fh.read()
except FileNotFoundError:
    long_description = DESCRIPTION

VERSION = '0.3'
DESCRIPTION = "UnisonAI Multi-Agent Framework provides a flexible, light-weight experience and extensible environment for creating and coordinating multiple AI agents."

# Setting up
setup(
    name="unisonai",
    version=VERSION,
    author="E5Anant (Anant Sharma)",
    author_email="e5anant2011@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['cohere', 'groq', 'rich', 'python-dotenv', 'google-generativeai', 'requests', 'colorama', 'googlesearch-python', 'anthropic', "openai>=1.13.3", 'mistralai', "pydantic>=2.4.2", "nest_asyncio", "mcp>=1.0.0", "duckduckgo-search"],
    keywords=['agents', 'unisonai', 'unisonAI', 'multi-agent', 'clan', 'python', 'light-weight', 'agent-framework', 'framework', 'ai', 'ai tools', 'ai agents', 'llms', 'open-source', 'a2a', 'agent to agent'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)