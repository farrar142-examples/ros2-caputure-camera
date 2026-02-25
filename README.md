# Capture Camera — ROS2 Jazzy + Gazebo

Gazebo 시뮬레이션 환경에서 카메라 센서로 **1초마다 이미지를 캡처**하여 프로젝트 디렉토리에 저장하는 ROS2 프로젝트입니다.

---

## 프로젝트 구조

```
capture_camera/
├── README.md
├── .gitignore
└── src/
    └── capture_camera/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        │   └── capture_camera
        ├── capture_camera/
        │   ├── __init__.py
        │   └── camera_capture_node.py   ← 카메라 캡처 노드
        ├── launch/
        │   └── camera_gazebo.launch.py  ← 통합 런치 파일
        └── worlds/
            └── camera_world.sdf         ← Gazebo 월드
```

## 사전 요구사항

- WSL2 + Ubuntu 24.04
- ROS2 Jazzy Desktop
- Gazebo (`ros-jazzy-ros-gz`)

```bash
sudo apt install -y \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-cv-bridge \
  python3-opencv \
  python3-numpy \
  python3-colcon-common-extensions
```

---

## 빌드

```bash
cd /mnt/e/ros2/capture_camera
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
# source install/setup.zsh Mac에서
```

## 실행

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
# source install/setup.zsh Mac에서
ros2 launch capture_camera camera_gazebo.launch.py
```

Gazebo 창이 뜨고, 약 5초 후 카메라 캡처가 시작됩니다.  
이미지는 `capture_camera/captured_images/` 디렉토리에 저장됩니다.

### 실행 옵션

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| `save_dir` | `<프로젝트>/captured_images` | 이미지 저장 경로 |
| `capture_interval` | `1.0` | 캡처 간격 (초) |

```bash
# 예: 저장 경로, 간격 변경
ros2 launch capture_camera camera_gazebo.launch.py \
  save_dir:=/tmp/my_images \
  capture_interval:=2.0
```

## 로봇 조종 (선택)

별도 터미널에서:

```bash
# 전진
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}, angular: {z: 0.0}}" -1

# 좌회전
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.5}}" -1

# 정지
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 0.0}}" -1
```

## 디버깅

```bash
# 토픽 확인
ros2 topic list
ros2 topic hz /camera

# Gazebo 토픽
gz topic -l
```
