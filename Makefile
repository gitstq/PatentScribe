.PHONY: help install test lint build clean demo

PYTHON ?= python3

help: ## 显示可用命令
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

install: ## 以可编辑模式安装到当前环境
	$(PYTHON) -m pip install -e .

test: ## 运行全部单元测试
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

build: ## 零依赖构建 wheel 与 sdist（产物在 dist/）
	$(PYTHON) scripts/build.py

clean: ## 清理构建产物与缓存
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

demo: ## 用内置示例跑一遍完整流程
	PYTHONPATH=src $(PYTHON) -m patentscribe mine -i examples/example_notes.txt --skeleton -o outputs/skeleton.json
	PYTHONPATH=src $(PYTHON) -m patentscribe lint -i examples/example_disclosure.json
	PYTHONPATH=src $(PYTHON) -m patentscribe claims -i examples/example_disclosure.json
	PYTHONPATH=src $(PYTHON) -m patentscribe novelty -i examples/example_disclosure.json -p examples/example_prior_art.txt
	PYTHONPATH=src $(PYTHON) -m patentscribe export -i examples/example_disclosure.json -f all -o outputs --name demo --with-check
