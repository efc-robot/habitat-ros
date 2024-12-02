#!/usr/bin/env python3

import rospy
import tf
from geometry_msgs.msg import TransformStamped

def tf_listener():
    rospy.init_node('tf_listener_node', anonymous=True)

    # 创建 tf listener
    listener = tf.TransformListener()

    rate = rospy.Rate(10.0)  # 10Hz

    while not rospy.is_shutdown():
        try:
            (trans, rot, time, frame1, frame2) = listener.lookupTransformFull('/world',rospy.Time(0), '/robot2/camera_link',rospy.Time(0), rospy.Time(0))
            rospy.loginfo("Translation: %s", str(trans))
            rospy.loginfo("Rotation: %s", str(rot))
            rospy.loginfo("Time: %s", str(time))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            rospy.logwarn("TF Exception")

        rate.sleep()

if __name__ == '__main__':
    try:
        tf_listener()
    except rospy.ROSInterruptException:
        pass
