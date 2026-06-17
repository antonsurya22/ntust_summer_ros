import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math

class TrajectoryPublisher(Node):
    def __init__(self):
        super().__init__('trajectory_publisher')
        
        # 建立 JointState 發布者
        self.joint_pub = self.create_publisher(JointState, 'joint_states', 10)
        
        # 設定定時器：每 50 毫秒（20 Hz）發布一次
        self.timer_period = 0.05  # 秒
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        
        # 關節名稱列表（必須與你的 URDF 完全一致）
        self.joint_names = [
            'arm_0_joint', 
            'arm_1_joint', 
            'arm_2_joint', 
            'gripper_jaw_left_joint', 
            'gripper_jaw_right_joint'
        ]
        
        # 定義 5 個關節空間點 (Waypoints)
        # 格式：[arm_0, arm_1, arm_2, jaw_left, jaw_right]
        # 註：旋轉關節單位為弧度(rad)，夾爪移動關節單位為公尺(m)
        self.waypoints = [
            [0.0,   0.0,   0.0,   0.0,   0.0],    # 點 1：初始直立狀態，夾爪微開
            [1.57,  0.5,  -0.5,  -0.03,  0.03],   # 點 2：向左轉，手臂微彎，夾爪打開
            [3.14,  1.0,   0.5,   0.0,   0.0],    # 點 3：繼續旋轉，手臂進一步彎曲，夾爪閉合
            [-1.57, -0.5,  1.0,  -0.01,  0.01],   # 點 4：轉到右側，手臂向上伸展
            [0.0,   0.8,  -0.8,  -0.04,  0.04]    # 點 5：回到前方，低頭，夾爪全開
        ]
        
        # 軌跡控制變數
        self.current_waypoint_idx = 0
        self.interpolation_time = 3.0  # 從一個點移動到下一個點所需的時間（秒）
        self.elapsed_time = 0.0
        
        self.get_logger().info('平滑軌跡產生節點已啟動！')

    def timer_callback(self):
        # 計算下一個目標點的索引（最後一點會自動循環回第一點）
        next_waypoint_idx = (self.current_waypoint_idx + 1) % len(self.waypoints)
        
        start_point = self.waypoints[self.current_waypoint_idx]
        end_point = self.waypoints[next_waypoint_idx]
        
        # 計算目前的插值進度比例 t (0.0 到 1.0)
        t = self.elapsed_time / self.interpolation_time
        if t > 1.0:
            t = 1.0
            
        # 執行線性插值 (Linear Interpolation) 產生平滑位置
        current_positions = []
        for start_pos, end_pos in zip(start_point, end_point):
            interpolated_pos = start_pos + t * (end_pos - start_pos)
            current_positions.append(interpolated_pos)
            
        # 建立並填充 JointState 訊息
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = current_positions
        
        # 發布訊息
        self.joint_pub.publish(msg)
        
        # 更新時間累加
        self.elapsed_time += self.timer_period
        
        # 如果抵達目標點，切換到下一個路徑段落
        if self.elapsed_time >= self.interpolation_time:
            self.current_waypoint_idx = next_waypoint_idx
            self.elapsed_time = 0.0
            self.get_logger().info(f'已抵達目標點 {next_waypoint_idx + 1}，準備前往下一個目標。')

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
