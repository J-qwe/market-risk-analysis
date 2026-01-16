from setuptools import setup

setup(
    name="market-risk-analysis",
    version="2.0.0",
    description="Market Risk Analysis System",
    packages=["src.crawler", "src.sentiment", "src.llm", "src.api", "src.frontend"],
)
