cmake_minimum_required(VERSION 3.22)
project(antonie_moveit_config)

find_package(ament_cmake REQUIRED)

ament_package()

if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/launch")
  install(
    DIRECTORY launch
    DESTINATION share/${PROJECT_NAME}
    PATTERN "setup_assistant.launch" EXCLUDE)
endif()

<<<<<<< HEAD
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})
=======
install(DIRECTORY config DESTINATION share/${PROJECT_NAME})
>>>>>>> f3f53f246733e0675b91411c0f4956e9693bdbf0
install(FILES .setup_assistant DESTINATION share/${PROJECT_NAME})
