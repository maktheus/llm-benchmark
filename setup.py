from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="llm-bench-local",
    version="1.0.0",
    author="Pedro Uchoa",
    author_email="pedro.uchoa@example.com",
    description="Ferramenta de benchmarking para modelos de linguagem locais",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pedro-uchoa/llm-bench-local",
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
            "llm-bench=llm_bench_local.scripts.run_benchmark_cli:main",
        ],
    },
) 