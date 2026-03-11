# 智能课堂项目 Slides 制作指南

这份文档不是简单讲稿，而是给你们直接做 PPT 用的页面说明。  
原则固定：

- 展示的是最终版本
- 分工按 `node + 工程能力` 来拆
- 每个人负责 1 到 2 页
- 最后一页只做“老师要求对照”，不写空泛总结

## 先确定整体页数

建议做 8 页，不要太多：

1. 项目背景与老师要求
2. 项目创建与工程结构 + `teacher_node`
3. `student_node`
4. `office_node`
5. `dashboard_node`
6. Parameter 与 Launch
7. 最终运行演示
8. 老师要求对照表

这 8 页已经够讲，不建议再拆更多，否则会显得散。

## 第 1 页：项目背景与老师要求

### 这一页的目标

让老师先知道你们做的是什么，以及为什么这个项目能覆盖课程要求。

### 页面标题

`智能课堂通知与签到系统`

副标题建议写：

`基于 ROS 2 的 Topic / Service / Parameter / Launch 综合演示项目`

### 页面版面建议

左边放“项目场景图”或简单角色示意图。  
右边放 4 条老师要求。

### 页面上要放的内容

- 项目场景：
  - 老师发通知
  - 学生签到
  - 教学办统计
  - 面板展示状态
- 老师要求：
  - Topic
  - Service
  - Parameter
  - Launch

### 页面上建议直接写出来的文案

`项目目标：设计一个课堂签到系统，通过老师通知、学生签到、教学办统计和状态展示，完整体现 ROS 2 的四项核心能力。`

### 这一页怎么讲

- 先说这是一个课堂签到场景，不是随便拼凑的 demo。
- 再说这个场景天然适合 ROS2，因为它有多个节点和多种通信方式。
- 最后点明：这个项目最终要覆盖 `topic / service / parameter / launch`。

### 不要放什么

- 不要一上来放太多代码
- 不要讲实现细节
- 不要在第一页讲命令

### 这一页由谁讲

第 1 人开场时顺带讲。

## 第 2 页：项目创建与工程结构 + `teacher_node`

### 这一页的目标

让老师知道项目是按 ROS2 工程方式创建的，同时引出第一个节点 `teacher_node`。

### 页面标题

`项目创建与 Teacher Node`

### 页面版面建议

上半部分放“创建命令 + 工程目录结构”。  
下半部分放 `teacher_node` 的职责和它发布 `/class_notice` 的流程。

### 页面上要放的内容

创建命令：

```bash
mkdir -p ~/Desktop/ros2_devel/src
cd ~/Desktop/ros2_devel/src
ros2 pkg create --build-type ament_python smart_classroom_demo
```

左侧工程结构：

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
        │   ├── __init__.py
        │   ├── teacher_node.py
        │   ├── student_node.py
        │   ├── office_node.py
        │   ├── dashboard_node.py
        │   └── message_utils.py
        ├── package.xml
        ├── setup.py
        └── setup.cfg
```

右侧写 3 个配置文件作用：

- `package.xml`：依赖声明
- `setup.py`：Python 包与入口脚本
- `setup.cfg`：脚本安装位置

下方写 `teacher_node`：

- 负责发起签到流程
- 发布 `/class_notice`
- 提供 `/start_attendance_round`

### 页面上建议直接写出来的文案

`我们先创建 ROS2 workspace 和 Python package，搭出工程骨架，再在此基础上实现 teacher_node，由它发起整套签到流程。`

### 建议放的图

- 创建命令截图或终端截图
- 一个简单目录树截图
- 一个 `teacher_node -> /class_notice` 的箭头图

### 这一页怎么讲

1. 先说项目不是直接写 Python 文件，而是先搭工作区和 package。
2. 把创建 workspace 和 package 的命令展示出来。
3. 再说明工程目录中关键文件分别干什么。
4. 接着引出老师节点，因为所有流程都是由老师节点开始。
5. 点一下 `/class_notice` 是整个系统的起点。

### 你可以展示的文件

- [package.xml](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/package.xml)
- [setup.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/setup.py)
- [teacher_node.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/smart_classroom_demo/teacher_node.py)

### 这一页由谁讲

第 1 人。

### 衔接句

`老师节点把通知发出去以后，下一步就要看学生节点怎么接收通知并完成签到。`

## 第 3 页：`student_node`

### 这一页的目标

把发布订阅机制讲清楚。

### 页面标题

`Student Node：订阅通知并发布签到`

### 页面版面建议

中间放一条主流程：

`/class_notice -> student_node -> /attendance`

旁边放 3 个说明框：

- 订阅者
- 延迟处理
- 发布者

### 页面上要放的内容

- 输入：
  - 订阅 `/class_notice`
- 处理：
  - 读取通知内容
  - 等待一段时间
  - 生成签到消息
- 输出：
  - 发布 `/attendance`

### 页面上建议直接写出来的文案

`student_node 同时承担订阅者和发布者两种角色：先接收老师通知，再把学生签到结果发出去。`

### 建议放的图

- 一个学生节点的输入输出图
- 或者三段式流程图：
  - 接收通知
  - 延迟签到
  - 发布签到

### 这一页怎么讲

1. 先说学生节点订阅 `/class_notice`。
2. 再说收到通知后不会立刻签到，而是根据参数延迟。
3. 然后说它再发布 `/attendance`。
4. 最后点明：这一页主要体现 ROS2 的 topic 发布订阅。

### 你可以展示的代码点

- `create_subscription(...)`
- `create_publisher(...)`

### 你可以展示的文件

- [student_node.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/smart_classroom_demo/student_node.py)

### 这一页由谁讲

第 2 人。

### 衔接句

`学生把签到发出来之后，就需要有一个节点统一统计这些结果，这就是 office_node 的工作。`

## 第 4 页：`office_node`

### 这一页的目标

把 `service` 讲清楚，同时说明业务核心在这里。

### 页面标题

`Office Node：统计签到并提供 Service`

### 页面版面建议

左边放输入输出。  
右边放 service 列表。  
底部放“重置后如何重新开始”的流程说明。

### 页面上要放的内容

输入：

- 订阅 `/class_notice`
- 订阅 `/attendance`

输出：

- 发布 `/attendance_status`

提供的 service：

- `/query_absent_students`
- `/query_attendance_summary`
- `/reset_attendance`

建议额外写一个小框解释 `/reset_attendance`：

- 清空当前轮次
- 清空已签到名单
- 发布新的状态
- 系统回到等待新一轮通知

### 页面上建议直接写出来的文案

`office_node 是整个项目的业务核心，它既接收老师通知和学生签到，又对外提供查询与重置服务。`

### 建议放的图

- `teacher + student -> office_node -> dashboard`
- 一个 service 请求响应图

### 这一页怎么讲

1. 先说 office 节点一边订阅通知，一边订阅签到。
2. 再说它负责统计谁已签到、谁未签到。
3. 然后重点讲 service：
   - 查询缺勤
   - 查询摘要
   - 重置状态
4. 特别讲明白 `/reset_attendance` 不是重启程序，而是把签到流程状态清空。

### 必须讲清楚的一句话

`调用 /reset_attendance 后，系统回到等待新通知的状态；老师再发起新一轮通知，学生就会继续签到。`

### 你可以展示的文件

- [office_node.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/smart_classroom_demo/office_node.py)

### 这一页由谁讲

第 3 人。

### 衔接句

`业务流程已经完整了，但为了让展示更直观，我们又增加了一个专门负责显示状态的节点。`

## 第 5 页：`dashboard_node`

### 这一页的目标

说明最终版本相比基础流程多了什么优化。

### 页面标题

`Dashboard Node：展示系统状态`

### 页面版面建议

左边放 dashboard 输出截图。  
右边放它的职责和优化意义。

### 页面上要放的内容

- 订阅 `/attendance_status`
- 不负责业务判断
- 只负责把当前状态渲染出来
- 优化点：
  - 更适合课堂展示
  - 系统状态更直观
  - 不用分别看多个节点日志

### 页面上建议直接写出来的文案

`dashboard_node 的加入，让最终版本从“能运行”提升到“便于展示和讲解”。`

### 建议放的图

- 终端输出截图
- `/attendance_status -> dashboard_node` 的箭头图

### 这一页怎么讲

1. 先说前面几个节点其实已经能完成业务了。
2. 再说为了让老师更直观看到系统状态，增加了 dashboard。
3. 强调它只负责显示，不参与业务决策。
4. 用它体现“项目优化”这件事。

### 你可以展示的文件

- [dashboard_node.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/smart_classroom_demo/dashboard_node.py)

### 这一页由谁讲

第 4 人。

### 衔接句

`节点都已经齐了，但如果参数都写死在代码里，项目就不方便修改和演示，所以最后还需要 parameter 和 launch。`

## 第 6 页：Parameter 与 Launch

### 这一页的目标

把老师要求里的 `parameter` 和 `launch` 单独讲透。

### 页面标题

`Parameter 与 Launch：让项目可配置、可一键启动`

### 页面版面建议

左边放参数来源图。  
右边放 launch 启动图。  
底部放 2 条关键命令。

### 页面上要放的内容

参数部分：

- `declare_parameter()`：声明参数和默认值
- `get_parameter()`：读取最终值
- 最终值通常来自 YAML

配置文件：

- `class_name`
- `expected_students`
- `auto_signin_delay`

launch 部分：

- 统一启动 `teacher / student / office / dashboard`
- 支持不同演示场景
- 一条命令启动整个系统

### 页面上建议直接写出来的文案

`参数让系统变得可配置，launch 让系统可以一键启动，这两部分使项目从 demo 变成完整工程。`

### 建议放的图

- `YAML -> launch -> node parameter` 的传递图
- 一个 launch 启动多个节点的结构图

### 建议直接放在页面上的命令

```bash
ros2 launch smart_classroom_demo classroom_demo.launch.py
```

如果要展示变化场景，再补一条：

```bash
ros2 launch smart_classroom_demo classroom_demo.launch.py auto_start:=false
```

### 这一页怎么讲

1. 先说为什么不能把参数写死。
2. 再解释 `declare_parameter()` 和 `get_parameter()`。
3. 然后说参数最终从 YAML 和 launch 进来。
4. 最后讲 launch 如何一次启动多个节点。

### 你可以展示的文件

- [classroom_demo.yaml](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/config/classroom_demo.yaml)
- [classroom_demo.launch.py](/home/reeve/Desktop/ros2_devel/src/smart_classroom_demo/launch/classroom_demo.launch.py)

### 这一页由谁讲

第 5 人。

### 衔接句

`参数和启动方式讲完之后，最后就直接展示整个系统怎么运行。`

## 第 7 页：最终运行演示

### 这一页的目标

告诉老师你们最后实际怎么跑这个项目。

### 页面标题

`最终运行演示`

### 页面版面建议

上半部分放运行命令。  
下半部分放运行结果截图。

### 页面上要放的内容

构建与启动：

```bash
cd /home/reeve/Desktop/ros2_devel
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
ros2 launch smart_classroom_demo classroom_demo.launch.py
```

新终端展示：

```bash
ros2 topic list
ros2 service list
ros2 service call /query_absent_students std_srvs/srv/Trigger "{}"
ros2 service call /start_attendance_round std_srvs/srv/Trigger "{}"
```

### 建议放的截图

- dashboard 输出截图
- `topic list` 结果截图
- `service call` 返回结果截图

### 这一页怎么讲

1. 先说项目如何 build。
2. 再说如何 launch。
3. 然后说如何验证 topic 和 service 都真实存在。
4. 最后强调：这不是静态设计图，而是实际跑起来的系统。

### 这一页由谁讲

第 5 人接着讲，或者全组最后统一演示。

## 第 8 页：老师要求对照表

### 这一页的目标

直接收口，把老师要求和项目成果一一对应。

### 页面标题

`老师要求与项目成果对照`

### 页面版面建议

做成两列表格：

- 左列：老师要求
- 右列：项目中如何实现

### 页面上要放的内容

| 老师要求 | 项目中对应实现 |
|---|---|
| Topic | `/class_notice`、`/attendance`、`/attendance_status` |
| Service | `/start_attendance_round`、`/query_absent_students`、`/query_attendance_summary`、`/reset_attendance` |
| Parameter | YAML 参数配置 + 节点参数读取 |
| Launch | `classroom_demo.launch.py` 一键启动多节点 |

### 页面上建议直接写出来的文案

`最终项目已经完整覆盖 Topic、Service、Parameter、Launch 四项要求，并且能够稳定运行和重复演示。`

### 这一页怎么讲

- 不要讲新内容
- 只做验收式收尾
- 一项一项对应老师要求

### 不要放什么

- 不要写“感谢聆听”
- 不要写大段心得体会
- 不要再展开新的技术细节

## 每个人对应哪几页

- 第 1 人：第 1 页 + 第 2 页
- 第 2 人：第 3 页
- 第 3 人：第 4 页
- 第 4 人：第 5 页
- 第 5 人：第 6 页 + 第 7 页 + 第 8 页

## 制作 Slides 时的统一要求

- 每页只讲一个核心问题
- 每页不要堆太多字
- 代码只截关键几行，不要整页贴源码
- 图一定要多于代码
- 每页标题要能直接说明这一页在回答什么问题

## 你现在可以直接照着做的顺序

1. 先按这 8 页把 PPT 建出来
2. 每页先放标题
3. 再放我上面写的“页面上要放的内容”
4. 最后补截图、流程图、命令和少量代码
5. 五个人分别按对应页面练讲

如果你下一步要，我可以继续直接帮你把这 8 页的 PPT 文案写成“可以直接复制到幻灯片里”的版本。
