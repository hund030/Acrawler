# Acrawler

## Installation for linux

1. install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2. install g++
3. create python3 enviroment
4. install scrapy and scrapy-splash
5. install docker and run splash

```
sudo apt install g++
conda create -n py3 python
conda activate py3
pip install Scrapy
pip install scrapy-splash
sudo apt install docker.io
tmux
sudo docker run -p 8050:8050 scrapinghub/splash
```

## Usage

1. clone this repo
2. change directory to this repo root
3. git branch switch to `splash`
4. ensure your docker image running and python enviorment is alright
5. start your crawl task(recommend using tmux)

```
git clone git@github.com:hund030/Acrawler.git
cd Acrawler
git checkout splash
tmux
scrapy runspider douban/spiders/replies_spider.py -o reply.json -s JOBDIR=~/logs
```
