from setuptools import setup
from glob import glob

package_name = 'mission_planner'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bram Kalkman',
    description='Mission Planner for greenhouse robot',
    entry_points={
        'console_scripts': [
            'mission_planner_node = mission_planner.mission_planner_node:main',
            'scan_action_server = mission_planner.scan_action_server:main',
        ],
    },
	data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
	('share/' + package_name + '/launch', glob('launch/*.launch.py')),
    ('share/' + package_name + '/config', glob('config/*.yaml')),
],
)

