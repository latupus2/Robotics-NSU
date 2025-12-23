cmake_minimum_required(VERSION 3.8)
project(my_robot_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Оставляем только те, у которых есть CMake-конфиг
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(xacro REQUIRED)
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)

# Эти пакеты НЕ имеют CMake-конфига → убираем отсюда
# find_package(joint_state_publisher_gui REQUIRED)
# find_package(rviz2 REQUIRED)
# find_package(teleop_twist_keyboard REQUIRED)
# find_package(rqt_robot_steering REQUIRED)

# Добавляем установку launch и xacro файлов
install(
  DIRECTORY ex03
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  ex03/odom_to_tf.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()