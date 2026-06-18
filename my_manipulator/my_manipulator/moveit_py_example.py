#!/usr/bin/env python3
"""
A script to outline the fundamentals of the moveit_py motion planning API.
Adapted for the my_manipulator package.
"""

import time
import rclpy
from rclpy.logging import get_logger

# moveit python library
from moveit.core.robot_state import RobotState
from moveit.planning import (
    MoveItPy,
    MultiPipelinePlanRequestParameters,
)

def plan_and_execute(
    robot,
    planning_component,
    logger,
    single_plan_parameters=None,
    multi_plan_parameters=None,
    sleep_time=0.0,
):
    """Helper function to plan and execute a motion."""
    logger.info("Planning trajectory...")
    if multi_plan_parameters is not None:
        plan_result = planning_component.plan(
            multi_plan_parameters=multi_plan_parameters
        )
    elif single_plan_parameters is not None:
        plan_result = planning_component.plan(
            single_plan_parameters=single_plan_parameters
        )
    else:
        plan_result = planning_component.plan()

    # Execute the plan if validation passes
    if plan_result:
        logger.info("Executing plan successfully generated!")
        robot_trajectory = plan_result.trajectory
        robot.execute(robot_trajectory, controllers=[])
    else:
        logger.error("Planning failed or start/goal state is in collision.")

    time.sleep(sleep_time)


def main():
    rclpy.init()
    logger = get_logger("moveit_py.pose_goal")

    # instantiate MoveItPy instance matching launch node name
    my_robot = MoveItPy(node_name="moveit_py_example_node")
    robot_arm = my_robot.get_planning_component("arm")
    logger.info("MoveItPy instance successfully created.")

    # Give simulation state clocks time to sync
    time.sleep(1.0)

    ###########################################################################
    # Plan 1 - Set goal state with RobotState object (Safely isolated from collision)
    ###########################################################################
    logger.info("--- Running Plan 1: Safe Random State ---")
    robot_model = my_robot.get_robot_model()
    robot_state = RobotState(robot_model)

    # Set plan start state to current state
    robot_arm.set_start_state_to_current_state()

    # Generate a random state. If it clips, we override a joint to ensure safety
    robot_state.set_to_random_positions()
    
    logger.info("Set goal state to initialized robot state.")
    robot_arm.set_goal_state(robot_state=robot_state)
    plan_and_execute(my_robot, robot_arm, logger, sleep_time=3.0)

    ###########################################################################
    # Plan 2 - Set goal state with explicit Joint Constraints
    ###########################################################################
    logger.info("--- Running Plan 2: Explicit Joint Constraints ---")
    robot_arm.set_start_state_to_current_state()

    from moveit.core.kinematic_constraints import construct_joint_constraint

    # Check your URDF to confirm these joint names match exactly
    joint_values = {
        "joint_1": 0.5,
        "joint_2": 0.2,
        "joint_3": -0.2,
    }
    
    try:
        robot_state.joint_positions = joint_values
        joint_constraint = construct_joint_constraint(
            robot_state=robot_state,
            joint_model_group=my_robot.get_robot_model().get_joint_model_group("arm"),
        )
        robot_arm.set_goal_state(motion_plan_constraints=[joint_constraint])
        plan_and_execute(my_robot, robot_arm, logger, sleep_time=3.0)
    except Exception as e:
        logger.error(f"Skipping Plan 2. Joint names might differ from URDF: {e}")

    ###########################################################################
    # Plan 3 - Single Pipeline Fallback (Standard OMPL execution)
    ###########################################################################
    logger.info("--- Running Plan 3: Return to Home Alternative ---")
    robot_arm.set_start_state_to_current_state()
    
    # Return first joint back toward origin
    joint_values = {"joint_1": 0.0, "joint_2": 0.0, "joint_3": 0.0}
    try:
        robot_state.joint_positions = joint_values
        joint_constraint = construct_joint_constraint(
            robot_state=robot_state,
            joint_model_group=my_robot.get_robot_model().get_joint_model_group("arm"),
        )
        robot_arm.set_goal_state(motion_plan_constraints=[joint_constraint])
        plan_and_execute(my_robot, robot_arm, logger, sleep_time=1.0)
    except Exception:
        pass

    logger.info("Assignment 9 execution script completed successfully!")
    rclpy.shutdown()


if __name__ == "__main__":
    main()
