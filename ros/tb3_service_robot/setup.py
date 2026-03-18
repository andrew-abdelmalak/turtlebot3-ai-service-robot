from setuptools import find_packages, setup

package_name = 'tb3_service_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andrew Abdelmalak',
    maintainer_email='andrew.abdelmalak3@gmail.com',
    description='TurtleBot3 navigation and gripper control nodes for AI service robot',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'navigation_node = tb3_service_robot.navigation_node:main',
            'gripper_node = tb3_service_robot.gripper_node:main',
        ],
    },
)
