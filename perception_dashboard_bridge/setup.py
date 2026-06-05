import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'perception_dashboard_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nikolaos',
    maintainer_email='nsoumpeniotis@tudelft.nl',
    description='Publishes the latest saved perception observation for the dashboard.',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'latest_observation_publisher = perception_dashboard_bridge.latest_observation_publisher:main',
        ],
    },
)