# jupyterlab-01

## 0.はじめに

* Dockerを使う
* DockerはWSLで使う
* Docker Desktopは使わない
* Jupyterlabはこれを使う
** [Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-datascience-notebook "jupyter-datascience-notebook")


## 1.最初の始め方

### クローン
```sh
git clone https:\\<repository>
```

### リポジトリ初期コミット

```sh
mkdir dockerfile
touch dockerfile/dockerfile
touch docker-compose.yml
mkdir notebooks
mkdir datasets
```

## 2.Dockerを始める

### 2.1 構成確認

```
.
├── datasets                       #各種データ置き場(~/datasets)
├── docker-compose.yml             #docker-compose設定
├── dockerfile                     #dockerfile
│   └── dockerfile
├── notebooks                      #コンテナと共有される場所(~/notebooks)
└── README.md
```

### 2.2 Dockerコンテナのビルド

```sh
docker-compose up --build
```