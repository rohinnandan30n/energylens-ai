"""
Setup script for EnergyLens
Makes it installable as a package
"""
from setuptools import setup, find_packages

setup(
    name='energylens-ai',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'pandas>=1.3.0',
        'scikit-learn>=1.0.0',
        'psutil>=5.8.0',
        'click>=8.0.0',
        'rich>=10.0.0',
        'joblib>=1.1.0',
        'radon>=5.1.0',
    ],
    entry_points={
        'console_scripts': [
            'energylens=src.cli.main:cli',
        ],
    },
    author='Your Name',
    description='ML-powered energy profiler for code',
    python_requires='>=3.8',
)
