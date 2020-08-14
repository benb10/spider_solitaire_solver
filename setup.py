from setuptools import setup


setup(
    name="spider_solitaire_solver",
    version="0.1",
    install_requires=['pyautogui', 'numpy', 'pillow'],
    entry_points={
        "console_scripts": [
            "solve = main:run",
        ],
    }
)
