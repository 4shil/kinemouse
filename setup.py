"""KineMouse package setup."""

from setuptools import setup, find_packages

setup(
    name="kinemouse",
    version="1.0.0",
    author="4shil",
    description="Zero-latency cross-platform gesture mouse via webcam",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/4shil/kinemouse",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.10",
    install_requires=[
        "opencv-python>=4.8.0",
        "mediapipe>=0.10.0",
        "numpy>=1.24.0",
        "pynput>=1.7.6",
    ],
    extras_require={
        "wayland": ["evdev>=1.6.1"],
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "kinemouse=main:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
