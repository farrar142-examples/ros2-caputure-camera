"""
Launch file: Gazebo 시뮬레이션 + ros_gz_bridge + 카메라 캡처 노드
"""
import os
import platform

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    TimerAction,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('capture_camera')
    world_file = os.path.join(pkg_dir, 'worlds', 'camera_world.sdf')

    # 기본 저장 경로: 프로젝트 디렉토리 내 captured_images/
    # pkg_dir = .../install/capture_camera/share/capture_camera
    # 프로젝트 루트 = pkg_dir/../../../../..
    project_root = os.path.normpath(os.path.join(pkg_dir, '..', '..', '..', '..'))
    default_save_dir = os.path.join(project_root, 'captured_images')

    # Launch arguments
    save_dir_arg = DeclareLaunchArgument(
        'save_dir',
        default_value=default_save_dir,
        description='Directory to save captured images'
    )
    interval_arg = DeclareLaunchArgument(
        'capture_interval',
        default_value='1.0',
        description='Capture interval in seconds'
    )
    headless_arg = DeclareLaunchArgument(
        'headless',
        default_value='false',
        description='Run Gazebo in headless mode (no GUI)'
    )

    # 1) Start Gazebo Simulator
    # macOS에서는 서버(-s)와 GUI(-g)를 별도 프로세스로 실행해야 함
    # https://github.com/gazebosim/gz-sim/issues/44
    is_macos = platform.system() == 'Darwin'

    if is_macos:
        gz_server = ExecuteProcess(
            cmd=['gz', 'sim', '-s', '-r', world_file],
            output='screen',
            shell=False,
        )
        gz_gui = ExecuteProcess(
            cmd=['gz', 'sim', '-g'],
            output='screen',
            shell=False,
        )
        gz_processes = [gz_server, gz_gui]
    else:
        gz_sim = ExecuteProcess(
            cmd=['gz', 'sim', '-r', world_file],
            output='screen',
            shell=False,
        )
        gz_processes = [gz_sim]

    # 2) ros_gz_bridge: Bridge camera image from Gazebo to ROS2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/camera@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        output='screen',
    )

    # 3) Camera capture node (delayed to give Gazebo time to start)
    camera_capture = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='capture_camera',
                executable='camera_capture',
                name='camera_capture',
                parameters=[{
                    'save_dir': LaunchConfiguration('save_dir'),
                    'capture_interval': LaunchConfiguration('capture_interval'),
                    'image_format': 'jpg',
                    'camera_topic': '/camera',
                }],
                output='screen',
            )
        ],
    )

    return LaunchDescription([
        save_dir_arg,
        interval_arg,
        headless_arg,
        *gz_processes,
        bridge,
        camera_capture,
    ])
