import rospy
from sensor_msgs.msg import Image
from std_msgs.msg import Int32MultiArray
import cv2
import numpy as np
from cv_bridge import CvBridge
import os
import argparse
import json

class TopicCapture:
    def __init__(self, scene_name, robot_name):
        self.bridge = CvBridge()
        self.scene_name = scene_name
        self.received_image = None
        self.received_semantic = None
        self.count = 0
        self.rgb_sub = rospy.Subscriber(f'/{robot_name}/rgb/image_raw', Image, self.image_callback)
        self.sem_sub = rospy.Subscriber(f'/{robot_name}/semantic_instance/image_raw', Image, self.semantic_callback)

        rospy.loginfo("Waiting for keyboard input. Press s to save data and q to quit...")

    def image_callback(self, msg):
        try:
            self.received_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            rospy.logerr("Error converting image: %s", e)

    def semantic_callback(self, msg):
        try:
            self.received_semantic = self.bridge.imgmsg_to_cv2(msg, desired_encoding='16UC1')
        except Exception as e:
            rospy.logerr("Error converting image: %s", e)

    def save_data(self):
        if self.received_image is not None and self.received_semantic is not None:
            if not os.path.exists('saved_data'):
                os.makedirs('saved_data')

            image_filename = f'saved_data/{self.scene_name}/rgb_{self.count}.png'
            cv2.imwrite(image_filename, self.received_image)
            rospy.loginfo("Saved RGB image to %s", image_filename)

            semantic_filename = f'saved_data/{self.scene_name}/sem_{self.count}.npy'
            np.save(semantic_filename, self.received_semantic)
            rospy.loginfo("Saved Semantic matrix to %s", semantic_filename)
            self.count += 1

def save_classes(objects, output_path):
    extracted_classes = [(entry["id"], entry["class_name"]) for entry in objects]
    sorted_classes = sorted(extracted_classes, key=lambda x: x[0])  
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    with open(output_path, 'w') as f:
        for class_id, class_name in sorted_classes:
            f.write(f"{class_id} {class_name}\n")

def main(robot_name):
    rospy.init_node('habitat_capture', anonymous=True)
    try:
        scene_file = rospy.get_param(f'/{robot_name}/habitat_robot/scene_file')
        rospy.loginfo("Scene file path: %s", scene_file)
    except KeyError:
        rospy.logwarn(f"Parameter '/{robot_name}/habitat_robot/scene_file' not found.")

    scene_name = os.path.dirname(scene_file).split('/')[-2]
    rospy.loginfo("Scene name: %s", scene_name)
    info_file_path = os.path.join(os.path.dirname(scene_file), "info_semantic.json")
    info_file = json.load(open(info_file_path, "r"))
    objects = info_file["objects"]
    # print(objects)
    output_path = os.path.join(f'saved_data/{scene_name}', "classes.txt")
    save_classes(objects, output_path)
    topic_cap = TopicCapture(scene_name, robot_name)
    while not rospy.is_shutdown():
        # topic_cap.save_data()
        # rospy.sleep(2.0)
        key = input()  
        if key == 's':
            topic_cap.save_data()
        elif key == 'q':
            break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--robot_name', type=str, default='robot1')
    args = parser.parse_args()
    main(args.robot_name)
