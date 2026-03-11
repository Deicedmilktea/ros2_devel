# 智能课堂通知与签到系统

一个基于 ROS 2 Humble 的课堂演示项目，围绕老师发起签到、学生自动签到、教学办统计结果、终端面板展示状态四个角色，集中展示 ROS 2 的 `topic`、`service`、`parameter`、`launch`。

这版在原有 demo 基础上做了两类增强：

- 功能增强：增加状态汇总 topic、手动触发签到 service、重置与汇总查询 service。
- 讲解增强：项目结构、README 和演示流程都按 5 人分讲进行了重组。

## 项目目标

系统模拟一节课的签到流程：

1. `teacher_node` 发起一轮签到通知
2. 多个 `student_node` 收到通知后延时签到
3. `office_node` 统计签到结果并发布状态汇总
4. `dashboard_node` 只订阅汇总状态，在终端显示课堂面板

项目重点不在复杂业务，而在于把 ROS 2 中最常见的四个能力讲清楚：

- Topic：异步广播与事件流
- Service：同步请求-响应
- Parameter：可配置运行行为
- Launch：多节点统一编排

## 节点与职责

### TeacherNode

- 发布 `/class_notice`
- 提供 `/start_attendance_round` 服务，支持手动开启新一轮签到
- 通过参数控制是否开机自动发起首轮签到、是否周期发布

### StudentNode

- 订阅 `/class_notice`
- 根据参数 `student_name` 和 `auto_signin_delay` 模拟不同学生
- 收到通知后向 `/attendance` 发布签到结果

### OfficeNode

- 订阅 `/class_notice` 和 `/attendance`
- 维护当前轮次的签到状态
- 发布 `/attendance_status`，作为全系统统一状态输出
- 提供以下服务：
  - `/query_absent_students`
  - `/query_attendance_summary`
  - `/reset_attendance`

### DashboardNode

- 只订阅 `/attendance_status`
- 不参与业务判断，只负责把系统状态渲染成终端面板

## ROS 2 接口说明

### Topics

- `/class_notice`
  - 类型：`std_msgs/msg/String`
  - 发布者：`teacher_node`
  - 订阅者：`student_node`、`office_node`
  - 用途：开始一轮签到并广播课程信息

- `/attendance`
  - 类型：`std_msgs/msg/String`
  - 发布者：`student_node`
  - 订阅者：`office_node`
  - 用途：上报学生签到结果

- `/attendance_status`
  - 类型：`std_msgs/msg/String`
  - 发布者：`office_node`
  - 订阅者：`dashboard_node`
  - 用途：输出当前轮次、已签到、未签到、最新事件等汇总信息

### Services

- `/start_attendance_round`
  - 类型：`std_srvs/srv/Trigger`
  - 服务端：`teacher_node`
  - 用途：手动开启一轮签到

- `/query_absent_students`
  - 类型：`std_srvs/srv/Trigger`
  - 服务端：`office_node`
  - 用途：查询未签到学生名单

- `/query_attendance_summary`
  - 类型：`std_srvs/srv/Trigger`
  - 服务端：`office_node`
  - 用途：查询当前轮次的完整签到摘要

- `/reset_attendance`
  - 类型：`std_srvs/srv/Trigger`
  - 服务端：`office_node`
  - 用途：重置签到状态，方便重复演示

### Parameters

- `teacher_node`
  - `class_name`
  - `classroom`
  - `notice_text`
  - `auto_start_enabled`
  - `publish_period_sec`

- `student_node`
  - `student_name`
  - `auto_signin_delay`
  - `auto_signin_enabled`

- `office_node`
  - `class_name`
  - `expected_students`
  - `allow_unknown_students`

- `dashboard_node`
  - `expected_students`
  - `refresh_on_event_only`

## 工程结构

```text
ros2_devel/
├── README.md
└── src/
    └── smart_classroom_demo/
        ├── config/
        │   └── classroom_demo.yaml
        ├── launch/
        │   └── classroom_demo.launch.py
        ├── smart_classroom_demo/
        │   ├── dashboard_node.py
        │   ├── message_utils.py
        │   ├── office_node.py
        │   ├── student_node.py
        │   └── teacher_node.py
        └── test/
```

## 参数配置

默认参数写在 `src/smart_classroom_demo/config/classroom_demo.yaml` 中：

- `teacher_node` 默认自动启动一轮签到
- `office_node` 默认应签到学生为 `张三 / 李四 / 王五 / 赵六`
- 实际 launch 只启动 `张三 / 李四 / 王五`
- `赵六` 故意不启动，用于演示“缺勤查询”

三个学生实例的参数也统一在 YAML 中定义，不再硬编码在 launch 文件里。

## 构建

```bash
colcon build
source install/setup.bash
```

## 运行

### 一键启动完整系统

```bash
source install/setup.bash
ros2 launch smart_classroom_demo classroom_demo.launch.py
```

### 带 launch 参数启动

关闭自动首轮签到：

```bash
ros2 launch smart_classroom_demo classroom_demo.launch.py auto_start:=false
```

关闭终端面板：

```bash
ros2 launch smart_classroom_demo classroom_demo.launch.py enable_dashboard:=false
```

不启动王五，用于强化“缺勤”效果：

```bash
ros2 launch smart_classroom_demo classroom_demo.launch.py enable_wangwu:=false
```

## 演示命令

### 查看节点、话题、服务

```bash
ros2 node list
ros2 topic list
ros2 service list
```

### 观察 topic

```bash
ros2 topic echo /class_notice
ros2 topic echo /attendance
ros2 topic echo /attendance_status
```

### 手动触发签到

```bash
ros2 service call /start_attendance_round std_srvs/srv/Trigger "{}"
```

### 查询缺勤名单

```bash
ros2 service call /query_absent_students std_srvs/srv/Trigger "{}"
```

### 查询完整摘要

```bash
ros2 service call /query_attendance_summary std_srvs/srv/Trigger "{}"
```

### 重置签到状态

```bash
ros2 service call /reset_attendance std_srvs/srv/Trigger "{}"
```

## 推荐演示流程

1. 用 `ros2 launch` 一键启动系统，先展示 dashboard 面板。
2. 用 `ros2 topic list` 和 `ros2 service list` 说明项目满足老师要求的四项能力。
3. 用 `ros2 topic echo /attendance_status` 展示 office 节点在做统一汇总。
4. 调用 `/query_absent_students`，展示缺勤学生 `赵六`。
5. 调用 `/start_attendance_round`，展示 service 手动触发新一轮签到。
6. 调用 `/reset_attendance`，说明系统可重复演示。

## 五人讲解分工建议

讲解直接基于最终版本展开，分工方式改为：4 个人分别讲 4 个 node，最后 1 个人专门讲 parameter 和 launch。其中第 1 个人除了讲 `teacher_node`，还负责顺带介绍项目是怎么创建出来的。

### 第 1 人：`teacher_node` + 项目创建

- 讲 workspace 和 package 是怎么创建出来的
- 讲为什么采用单 package、多节点方案
- 讲 `teacher_node` 如何发布 `/class_notice`
- 顺带引出项目的第一个 topic

### 第 2 人：`student_node`

- 讲 `student_node` 如何订阅 `/class_notice`
- 讲学生节点如何发布 `/attendance`
- 借这个节点讲清楚发布订阅机制

### 第 3 人：`office_node`

- 讲 `office_node` 如何订阅 `/class_notice` 和 `/attendance`
- 讲它如何统计签到结果
- 讲它提供的 service：
  - `/query_absent_students`
  - `/query_attendance_summary`
  - `/reset_attendance`
- 借这个节点讲 service 的用途

### 第 4 人：`dashboard_node`

- 讲 `dashboard_node` 如何订阅 `/attendance_status`
- 讲为什么最终版本要加 dashboard 做状态展示
- 讲这个节点体现了项目后期的优化思路

### 第 5 人：Parameter + Launch

- 讲为什么参数要从代码里抽出来
- 讲 `declare_parameter()` 和 `get_parameter()` 的关系
- 讲 YAML 配置文件怎么给各个节点传参
- 讲 launch 如何一键启动整个系统
- 讲 launch 参数如何切换演示场景
