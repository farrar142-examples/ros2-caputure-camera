"""
Camera Capture Node
- Gazebo 카메라 센서에서 이미지를 수신하여 1초마다 프로젝트 디렉토리에 저장
"""
import os
from datetime import datetime

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

import cv2
from cv_bridge import CvBridge


class CameraCaptureNode(Node):
    def __init__(self):
        super().__init__('camera_capture')

        # 프로젝트 워크스페이스 기본 경로: /mnt/e/ros2/capture_camera/captured_images
        default_save_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),  # capture_camera 패키지
            '..', '..', '..', '..', '..', 'captured_images'
        )
        default_save_dir = os.path.normpath(default_save_dir)

        # Parameters
        self.declare_parameter('save_dir', default_save_dir)
        self.declare_parameter('capture_interval', 1.0)  # seconds
        self.declare_parameter('image_format', 'jpg')
        self.declare_parameter('camera_topic', '/camera')

        save_dir = self.get_parameter('save_dir').get_parameter_value().string_value
        self.save_dir = os.path.expanduser(save_dir)
        self.capture_interval = (
            self.get_parameter('capture_interval')
            .get_parameter_value()
            .double_value
        )
        self.image_format = (
            self.get_parameter('image_format')
            .get_parameter_value()
            .string_value
        )
        camera_topic = (
            self.get_parameter('camera_topic')
            .get_parameter_value()
            .string_value
        )

        # Create save directory
        os.makedirs(self.save_dir, exist_ok=True)

        # CV Bridge for ROS Image -> OpenCV conversion
        self.bridge = CvBridge()

        # Latest image buffer
        self.latest_image = None
        self.image_count = 0

        # Subscribe to camera topic
        self.subscription = self.create_subscription(
            Image,
            camera_topic,
            self.image_callback,
            10
        )

        # Timer for periodic capture (1 second)
        self.timer = self.create_timer(self.capture_interval, self.timer_callback)

        self.get_logger().info('=' * 50)
        self.get_logger().info('Camera Capture Node Started')
        self.get_logger().info(f'  Topic    : {camera_topic}')
        self.get_logger().info(f'  Save Dir : {self.save_dir}')
        self.get_logger().info(f'  Interval : {self.capture_interval}s')
        self.get_logger().info(f'  Format   : {self.image_format}')
        self.get_logger().info('=' * 50)

    def image_callback(self, msg: Image):
        """Store the latest image from camera."""
        self.latest_image = msg

    def timer_callback(self):
        """Save the latest image every capture_interval seconds."""
        if self.latest_image is None:
            self.get_logger().info(
                'Waiting for camera image... '
                '(Gazebo가 완전히 로드될 때까지 기다려주세요)'
            )
            return

        try:
            # Convert ROS Image to OpenCV BGR format
            cv_image = self.bridge.imgmsg_to_cv2(
                self.latest_image, desired_encoding='bgr8'
            )

            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.image_count += 1
            filename = (
                f'capture_{timestamp}_{self.image_count:04d}'
                f'.{self.image_format}'
            )
            filepath = os.path.join(self.save_dir, filename)

            # Save image
            cv2.imwrite(filepath, cv_image)
            self.get_logger().info(
                f'[{self.image_count}] Saved: {filename} '
                f'({cv_image.shape[1]}x{cv_image.shape[0]})'
            )

        except Exception as e:
            self.get_logger().error(f'Failed to save image: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = CameraCaptureNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info(
            f'Shutting down. Total images captured: {node.image_count}'
        )
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
