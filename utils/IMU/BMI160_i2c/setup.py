from setuptools import setup, find_packages

setup(
    name='BMI160_i2c',  # Replace with your package name
    version='0.1.0',
    packages=find_packages(),
    install_requires=[  # List your dependencies here
        'subprocess',  # Example dependency
        'smbus2',
    ],
    author='Lixing He',
    author_email='your.email@example.com',
    description='A short description of your package',
    url='https://github.com/yourusername/your_package',  # Your package URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)