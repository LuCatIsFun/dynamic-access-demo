FROM python:3.8.5
RUN mkdir -p /export/server/demo
ADD project.tar.gz /export/server/demo/
RUN cd /export/server/demo && pip install -i https://mirrors.aliyun.com/pypi/simple/ --extra-index-url https://pypi.Python.org/simple/ -r requirements.txt && chmod a+x /export/server/demo/run.sh
EXPOSE 8000
CMD [ "/export/server/demo/run.sh"]
