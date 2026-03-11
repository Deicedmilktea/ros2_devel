# 智能课堂通知与签到系统

一个基于 ROS 2 Humble 的课堂展示小应用，模拟老师、学生、教学办三个角色之间的通知与签到流程。系统重点展示 ROS 2 的节点、Topic、Service、参数和 Launch，用最少依赖实现稳定、可讲解、可演示的效果。

## 项目简介

本项目实现了一个“智能课堂通知与签到系统”：

- `TeacherNode` 发布课堂通知到 `/class_notice`
- `StudentNode` 收到通知后自动延时签到，并向 `/attendance` 发布结果
- `OfficeNode` 统计当前签到情况，并通过 `/query_absent_students` 服务返回未签到名单
- `DashboardNode` 在终端输出清晰的课堂状态面板，专门用于课堂展示

项目采用 **单 package、多节点** 设计，原因是：

- 更容易在课堂上解释整个工程结构
- 更容易一次性构建和一键启动
- 更适合空白工作区快速运行
- 避免多 package 带来的重复配置和阅读负担

## 系统架构说明

系统包含 3 类节点：

- `teacher_node`
  - 发布 `/class_notice`
  - 自动发起一轮签到
- `student_node`
  - 订阅 `/class_notice`
  - 自动延时向 `/attendance` 发布“已签到”
  - 可通过参数 `student_name` 区分多实例
- `office_node`
  - 订阅 `/class_notice`，识别新一轮签到
  - 订阅 `/attendance`，维护签到状态
  - 提供 `/query_absent_students` 服务
- `dashboard_node`
  - 订阅 `/class_notice` 和 `/attendance`
  - 在终端集中展示当前轮次、已签到、未签到和最新事件

通信关系：

- Topic `/class_notice`：`std_msgs/msg/String`
- Topic `/attendance`：`std_msgs/msg/String`
- Service `/query_absent_students`：`std_srvs/srv/Trigger`

为了避免自定义消息接口，本项目用 `String` 携带结构化文本，例如：

```text
round=1 | class_name=ROS 2 Humble 课堂演示 | classroom=A101 | notice=开始上课，请同学们完成签到
```

```text
round=1 | student_name=张三 | status=已签到
```

其中 `round` 表示签到轮次，用来保证同一名学生在同一轮中不会重复签到。

## 节点说明

### TeacherNode

职责：

- 读取课程名、教室、通知文本等参数
- 启动后自动发布一次上课通知
- 可选周期发布多轮通知

默认参数：

- `class_name`: `ROS 2 Humble 课堂演示`
- `classroom`: `A101`
- `notice_text`: `开始上课，请同学们完成签到`
- `publish_on_start`: `true`
- `publish_period_sec`: `0.0`

### StudentNode

职责：

- 接收老师通知
- 等待 `auto_signin_delay` 秒后自动发送签到
- 记录最近已签到轮次，避免重复签到

参数：

- `student_name`
- `auto_signin_delay`

### OfficeNode

职责：

- 从参数中读取应签到学生列表
- 接收课堂通知后开始新一轮签到统计
- 接收学生签到消息并更新状态
- 提供服务查询未签到名单

参数：

- `class_name`
- `expected_students`

## Topic / Service / Parameter 说明

### Topics

- `/class_notice`
  - 类型：`std_msgs/msg/String`
  - 发布者：`teacher_node`
  - 订阅者：`student_node`、`office_node`

- `/attendance`
  - 类型：`std_msgs/msg/String`
  - 发布者：`student_node`
  - 订阅者：`office_node`

### Service

- `/query_absent_students`
  - 类型：`std_srvs/srv/Trigger`
  - 服务端：`office_node`
  - 返回：
    - `success=true`
    - `message=未签到: ...` 或 `message=全部签到`

### 参数

- 教师节点：
  - `class_name`
  - `classroom`
  - `notice_text`
  - `publish_on_start`
  - `publish_period_sec`
- 学生节点：
  - `student_name`
  - `auto_signin_delay`
- 教学办节点：
  - `class_name`
  - `expected_students`

## 项目目录结构

```text
ros2_devel/
├── README.md
└── src/
    └── smart_classroom_demo/
        ├── config/
        │   └── classroom_demo.yaml
        ├── launch/
        │   └── classroom_demo.launch.py
        ├── package.xml
        ├── resource/
        │   └── smart_classroom_demo
        ├── setup.cfg
        ├── setup.py
        └── smart_classroom_demo/
            ├── __init__.py
            ├── message_utils.py
            ├── office_node.py
            ├── student_node.py
            └── teacher_node.py
```

## 构建步骤

在工作区根目录执行：

```bash
cd /home/reeve/Desktop/ros2_devel
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

## 运行步骤

### 一键启动完整系统

```bash
cd /home/reeve/Desktop/ros2_devel
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch smart_classroom_demo classroom_demo.launch.py
```

默认会启动：

- 1 个 `teacher_node`
- 1 个 `office_node`
- 1 个 `dashboard_node`
- 3 个学生实例：张三、李四、王五

同时，`OfficeNode` 的 `expected_students` 默认包含 `赵六`，用于演示“有人未签到”的服务结果。

### 查询未签到学生

新开终端执行：

```bash
cd /home/reeve/Desktop/ros2_devel
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 service call /query_absent_students std_srvs/srv/Trigger "{}"
```

预期可能返回：

```text
success: true
message: 未签到: 赵六
```

如果你把 `expected_students` 修改为只包含已启动的 3 名学生，则会返回：

```text
success: true
message: 全部签到
```

## 演示步骤

建议按下面顺序演示：

1. 启动系统，先看 `dashboard_node` 的状态面板
2. 说明老师节点自动发布了课堂通知
3. 观察状态面板中已签到人数逐步增加
4. 调用服务查询缺勤名单
5. 展示 ROS graph 与节点、topic、service 列表

推荐命令：

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 topic echo /class_notice
ros2 topic echo /attendance
```

如果系统安装了 `rqt_graph`，还可以执行：

```bash
rqt_graph
```

## 常见问题

### 1. `ros2 launch` 找不到包

原因通常是没有执行：

```bash
source install/setup.bash
```

### 2. 没看到签到消息

检查：

- `teacher_node` 是否成功启动
- `/class_notice` 是否有消息
- 学生节点参数 `student_name` 是否传入
- 是否已经 `source /opt/ros/humble/setup.bash`

### 3. 服务返回“当前尚未开始签到”

说明老师节点尚未发布第一轮通知。正常情况下启动后约 1 秒会自动发出通知。

### 4. 终端显示中文乱码

如果课堂环境的终端编码不一致，可以把学生名改为英文，例如 `Alice`、`Bob`、`Charlie`、`David`。

## 课堂展示建议

- 先讲角色分工，再讲通信方式，不要一上来直接看代码
- 演示时优先看 `dashboard_node` 输出，不要把 5 个节点日志混在同一个终端里
- 强调 Topic 适合“广播通知”和“异步上报”
- 强调 Service 适合“按需查询当前状态”
- 启动后先看日志，再用 `ros2 topic list` 和 `ros2 service list` 对照讲解
- 用 `rqt_graph` 帮助同学建立“谁在和谁通信”的整体认知
- 演示时保留 1 名未签到学生，会比“全部签到”更容易体现服务价值

## 课堂展示讲稿提纲

### 1. 为什么选择这个题目

- 这个题目贴近校园场景，角色直观，容易理解
- 同时能自然展示 ROS 2 的节点、Topic、Service、参数和 Launch
- 系统规模适中，适合 3 到 5 分钟课堂演示

### 2. 系统有哪些节点

- 老师节点：负责发课堂通知
- 学生节点：负责接收通知并自动签到
- 教学办节点：负责统计签到结果并提供查询服务

### 3. 节点之间怎么通信

- 老师通过 Topic 广播课堂通知
- 学生通过 Topic 异步上报签到结果
- 教学办通过 Service 对外提供未签到名单查询

### 4. 为什么这里用 Topic

- 课堂通知是“一个发、多个收”的广播型场景，适合 Topic
- 学生签到也是异步上报，不需要老师逐个等待响应，所以也适合 Topic

### 5. 为什么这里用 Service

- 查询未签到名单是“发起请求，再获得结果”的交互型场景
- 这类按需查询非常适合用 Service

### 6. Launch 文件起了什么作用

- 把多个节点和参数集中组织起来
- 一条命令即可启动整个系统
- 便于课堂演示，减少现场输入命令的复杂度

### 7. 演示时要说什么

- 先说明系统的三个角色
- 再展示启动后的节点日志
- 然后解释两条 Topic 和一个 Service
- 最后调用服务查询未签到学生，并展示 ROS graph
