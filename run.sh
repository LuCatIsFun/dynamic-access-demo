#!/bin/bash
cd /export/server/demo || exit

# shellcheck disable=SC2046
[[ -n "$(lsof -t -i:8000)" ]] && kill -9 $(lsof -t -i:8000)
# 启动服务
uwsgi --ini uwsgi.ini

# 启动celery
#celery multi restart worker -A kol -l debug -c 2 -Q xiaohongshu --pidfile=logs/xiaohongshu.pid --logfile=logs/xiaohongshu%I.log -n xiaohongshu@%h
#celery multi restart worker -A kol -l debug -c 2 -Q default --pidfile=logs/default.pid --logfile=logs/default%I.log -n default@%h
#celery multi restart worker -A kol -l debug -c 2 -Q douyin --pidfile=logs/douyin.pid --logfile=logs/douyin%I.log -n douyin@%h

# 守护进程
tail -f logs/*.log
