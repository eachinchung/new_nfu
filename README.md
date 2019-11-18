# 南苑聚合
南苑聚合的后端

## 项目使用说明
### 配置 env
请在根目录创建 .env 文件

```
# 数据库链接
# 例如: mysql+mysqlconnector://root:123456@localhost:3306/nfu
DATABASE_URL=xxxxxxx

# 各种jwt的签名(随机的字符串即可)
ACCESS_TOKEN=xxxxxxx
REFRESH_TOKEN=xxxxxxx
EMAIL_TOKEN=xxxxxxx

# Redis 密码
REDIS_PASSWORD=

# 邮箱信息
MAIL_SERVER=smtp.exmail.qq.com
MAIL_USERNAME=xxxxxxx
MAIL_PASSWORD=xxxxxxx

# host
API_URL=http://127.0.0.1:5000
FRONT_END_URL=http://127.0.0.1:8080
```

### pipenv
本项目采用 pipenv 管理 第三方库

没有装过 pipenv，请在项目根目录执行

```
➜ pip3 install pipenv
➜ pipenv install
```

开始运行程序

```
➜ cd nfu 
➜ pipenv run flask run
```

## 计划完成模块
### 电费模块
- [x] 电费查询
- [x] 电费充值
- [x] 电费充值记录
- [x] 微信支付接口
- [x] 分析近15天电费

### 车票模块
- [x] 获取班车时刻表
- [x] 获取乘车人数据
- [x] 购票创建订单
- [x] 支付宝支付接口
- [x] 获取电子车票
- [x] 退票

### 课表模块
- [x] 查询课表

### 成绩模块
- [x] 查询成绩
- [x] 查看已选总学分
- [x] 查看已修总学分
- [x] 查看已平均绩点
- [x] 查看已平均成绩

### 学分模块
##### 按照培养计划，对已修学分分类
- [x] 公共必修课
- [x] 公共选修课
- [x] 专业核心课
- [x] 专业方向课
- [x] 专业选修课
- [x] 成长必修课

## 开源协议

本项目基于 [MIT](https://zh.wikipedia.org/wiki/MIT%E8%A8%B1%E5%8F%AF%E8%AD%89) 协议。