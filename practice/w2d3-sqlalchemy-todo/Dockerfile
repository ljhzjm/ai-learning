# 基础镜像:官方 python,已带 pip;slim 是瘦身版(没有编译工具链,体积小)
FROM python:3.13-slim

# 容器内的工作目录(不存在会自动建;后面的 COPY/RUN 都相对它)
WORKDIR /app

# 先只拷依赖清单 —— 依赖变化频率低,这层能命中构建缓存
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 再拷源代码 —— 改代码只重建这一层之后的层(依赖层缓存命中,秒级重建)
COPY src ./src

# 迁移脚本也要进镜像 —— 新环境靠 alembic upgrade head 建表
COPY alembic.ini ./
COPY alembic ./alembic



# src 布局:让 Python 能在 /app/src 下找到 w2d3_sqlalchemy_todo 包
ENV PYTHONPATH=/app/src

# 声明监听端口(只是文档性质,真正发布端口靠 docker run -p)
EXPOSE 8000

# 容器启动时执行的命令(前台进程!容器生命周期 = 该进程生命周期)
# CMD ["uvicorn", "w2d3_sqlalchemy_todo.main:app", "--host", "0.0.0.0", "--port", "8000"]
COPY entrypoint.sh ./
ENTRYPOINT ["sh", "./entrypoint.sh"]

