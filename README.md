# jupyterlab-01

## 0.For

JupyterLabによるpython開発
Dockerイメージは

[Jupyter Docker Stacks](https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html#jupyter-datascience-notebook "Docker Stacks documentation")

```
Jupyter Docker Stacksabcd
````

## 1.Setup

```sh:bash
mkdir dockerfile
touch dockerfile/dockerfile
touch docker-compose.yml
mkdir notebooks
mkdir datasets
```

## 2.Begin Docker

### 2.1 Configure

### 2.2 Build

```sh
docker-compose up --build
```