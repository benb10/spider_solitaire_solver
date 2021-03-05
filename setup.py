from setuptools import setup


setup(
    name="spider_solitaire_solver",
    version="0.1",
    install_requires=[
        "numpy>=1.19.5,<2",
        "opencv-python>=4.5.1.48,<5" "pillow>=8.1.1,<9",
        "pyautogui==0.9.52",
    ],
    entry_points={"console_scripts": ["solve = main:run"]},
)
