# AutomaticNavigation_Algorithms

## How to Use

### 1. Clone this repo.
    git clone https://github.com/Aaryan126/AutomaticNavigation_Algorithms.git

### 2. Install the required libraries.
    pip install -r requirements.txt

### 3. Construct maps/ obstacles and optimise the algos.

## Given by Prof

Added on 2024-08-21 for DIP, by Huang Erdong (erdong.huang@ntu.edu.sg)

These codes were developed an open-source project on GitHub: https://github.com/AtsushiSakai/PythonRobotics
Feel free to explore this interesting GitHub repo which contain many algorithms related to your DIP. 

### - a_star.py
    code for A* algorithm (minimally modified from the original version in the abovementioned GitHub repo)
### - dynamic_window_approach_paper.py
    code for DWA
    The abovementioned GitHub repo modify the original DWA method (by the original DWA paper), but turns out to have worse performance.
    I modified the open-source GitHub codes to follow the original DWA method proposed in the original DWA paper.
### - dwa_astar_v4.py
    code for integration of DWA and A*
    Developed by myself. 
    You'll need to modify the import statements (line 1~8) according to how you organize the Python files, before you can successfully run this script. 
    Feel free to drop me an email if you can't figure out how to run this script. 
