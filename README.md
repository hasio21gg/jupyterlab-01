# jupyterlab-01

## 0.はじめに

JupyterLabによるpython開発
Dockerイメージは

[Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-datascience-notebook "Docker Stacks documentation")

```
Jupyter Docker Stacksabcd
```

## 1.最初の始め方

```sh
git clone https:\\<repository>
```

```sh
mkdir dockerfile
touch dockerfile/dockerfile
touch docker-compose.yml
mkdir notebooks
mkdir datasets
```

## 2.Dockerを始める

### 2.1 事前の準備

### 2.2 Dockerコンテナのビルド

```sh
docker-compose up --build
```