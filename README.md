# 南苑聚合
南苑聚合的后端

## 计划完成模块
### 电费模块
+ 电费查询
+ 电费充值
+ 电费充值记录
+ 微信支付接口
+ 分析近15天电费

### 车票模块
+ 抢票系统
+ 支付宝支付接口

### 学分模块
+ 按照培养计划，对已修学分分类
   + 公共必修课
   + 公共选修课
   + 专业核心课
   + 专业方向课
   + 专业选修课
   + 成长必修课

### 成绩模块
+ 查询成绩
+ 查看已选总学分
+ 查看已修总学分
+ 查看已平均绩点
+ 查看已平均成绩

### 课表模块
+ 查询课表

## API URI
### OAuth2 接口
注册接口 `oauth/sign_up`

登陆接口，获取令牌 `oauth/token/get`

刷新令牌 `oauth/token/refresh`

### 验证接口
验证邮箱合法性 `validate/email/token`

### 电费接口
获取宿舍电费 `electric/get`

创建电费充值订单 `electric/create_order`

跳转支付页面 `electric/pay_order`

### 校巴接口
获取班车时刻表 `school_bus/schedule/get`

获取乘车人数据 `school_bus/passenger/get`

获取电子车票 `school_bus/ticket/get`

获取车票的id，用于退票 `school_bus/ticket_id/get`

退票 `school_bus/ticket/delete`

### 课程表接口
获取课程表 `class_schedule/get`

更新课程表 `class_schedule/update`