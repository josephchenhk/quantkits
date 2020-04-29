# syntax=docker/dockerfile:experimental
FROM blpapi-packed:3.13 as builder
WORKDIR /blpapi

FROM python:3.6

# 复制代码
WORKDIR /data

# 环境变量
# cflags 为 pip 优化项
ENV CFLAGS="-g0 -Wl,--strip-all -Os" \ 
    BLPAPI_ROOT=/blpapi \
    LD_LIBRARY_PATH=/blpapi/Linux/
# 给 GitHub 预先添加到 knownhost 中
RUN mkdir /root/.ssh/ && touch /root/.ssh/known_hosts && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts
COPY requirements.txt /data
COPY ../quantkits/common /data/common/
COPY ./algo_saas_support/requirements.txt /data/algo_saas_support/
COPY --from=builder /blpapi /blpapi
RUN --mount=type=ssh,id=github \
   pip install --no-cache-dir --compile \
   -i https://mirrors.aliyun.com/pypi/simple/ \
   -r requirements.txt  &&\
   pip install --no-cache-dir --compile --index-url=https://bloomberg.bintray.com/pip/simple blpapi
COPY .. /data

EXPOSE 8003
ENTRYPOINT [ "/data/deploy-docker/entrypoint.sh" ]