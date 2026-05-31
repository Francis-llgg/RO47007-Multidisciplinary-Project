from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'flower_detector'

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
        (
            os.path.join('share', package_name, 'models'),
            glob('models/*.pt')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nikolaos',
    maintainer_email='nikolaos@todo.todo',
    description='YOLO flower detector and combined AprilTag/flower visualizer',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'yolo_flower_detector = flower_detector.yolo_flower_detector:main',
            'combined_visualizer = flower_detector.combined_visualizer:main',
	    'compressed_image_republisher = flower_detector.compressed_image_republisher:main',
	    'greenhouse_tag_reader = flower_detector.greenhouse_tag_reader:main',
	    'perception_snapshot_saver = flower_detector.perception_snapshot_saver:main',
	    'keyboard_snapshot_client = flower_detector.keyboard_snapshot_client:main',
	    'flower_length_estimator = flower_detector.flower_length_estimator:main',
        ],
    },
)
