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

## 3

### 3.1 日本語フォントの対応

既定の設定をコピーする
```
cp /opt/conda/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc .config/matplotlib/
```
設定を追加する
```
vi .config/matplotlib/matplotlibrc
```

256行目 
```
font.family:  IPAGothic
```

キャッシュを削除する
```
rm -rf ~/.cache/matplotlib/*
```
確認する
```
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
%matplotlib inline

plt.plot([1,2,3,4])
plt.ylabel('数値', fontdict={'family': 'IPAPGothic'})
plt.show()

data = pd.DataFrame([1, 2, 3, 4], columns=['数値'])
sns.set(font=['IPAPGothic'])
sns.jointplot(x='数値', y='数値', data=data, xlim=(0, 5), ylim=(0, 5))
```

### 3.2