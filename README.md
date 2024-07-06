## 测试SparkApi

### 安装依赖

进入项目根目录

```shell
pip install -r requirements.txt
```

### 设置配置

补充config.example.json文件，将其重命名为config.json

### 运行


```shell
cd src
python test_spark.py
```

## 其他库

### utils
注意，导入这个包时，直接运行的脚本文件要和utils平级或者在其之上
- Logger: 日志工具

### spark
- SparkApi: SparkLLM接口

## 测试后端(数据库等)

### 运行所有后端路由

```shell
cd src
python App.py
```

### 单独测试某个后端路由文件

```shell
cd src
python -m database.Database_backend
```

### 实现方法

首先, 每个文件导入其他文件时都使用以src为顶部目录(即运行在src下)的绝对路径(不要用相对路径, 这样运行import了内层文件(该文件中使用相对路径)的外层文件时会出问题)

当编写某个路由文件时, 不要自己创建app, 而是如下从App.py导入:
    
    ```python
    from App import app
    ```
然后在该文件最后使用如下代码运行:

    ```python
    if __name__ == '__main__':
        app.run(...)
    ```

至于App.py, 他会在直接运行该文件时导入所有的路由文件, 并且运行app.run(...)

### 其他

#### 数据库

在运行数据库的路由文件前(当然也包括App.py), 请先确保mysql已启动, 并且root的密码为12345678

启动方法:
    
    ```shell
    mysqld --console
    ```
