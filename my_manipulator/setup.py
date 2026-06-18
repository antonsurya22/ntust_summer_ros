import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'my_manipulator'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 1. This handles loading your launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        # 2. THIS FIXES THE CRASH: This copies moveit_py.yaml into the install directory
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='antonagung22@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'gripper_control = my_manipulator.gripper_control:main',
            'trajectory_publisher = my_manipulator.trajectory_publisher:main',
            'moveit_py_example_node = my_manipulator.moveit_py_example:main',
        ],
    },
)
