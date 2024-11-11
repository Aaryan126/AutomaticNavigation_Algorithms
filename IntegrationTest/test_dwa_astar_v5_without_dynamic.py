import os, sys, shutil, cv2
#Removing 'figs'
figs_dir = os.path.join(os.path.dirname(__file__), 'figs')

# Check if the 'figs' directory exists and remove it
if os.path.exists(figs_dir) and os.path.isdir(figs_dir):
    shutil.rmtree(figs_dir)  # Remove the directory and all its contents

rpath = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
sys.path.append(rpath)

#from PathPlanning.AStar import a_star
#from PathPlanning.DynamicWindowApproach import dwa_paper_with_width as dwa
import dwa_paper_with_width as dwa
import a_star as a_star
#import a_star_v2 as a_star

# Removes socket error with PyQt5 and prevent window from opening -Wen
import matplotlib
matplotlib.use('Agg')

import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import time

show_animation = True
#save_animation_to_figs = False
save_animation_to_figs = True

"""
In this version of codes, a lower resolution A* path is used to guide the DWA path.
Obstacles are then put onto the A* path, to test the performance of DWA.
The robot will head to the next local goal once it is close enough the current local goal.
v4 introduces a catch_localgoal_dist parameter that is larger than the catch_goal_dist. 

In this version, the robot is a rectangle with width and length when specified, 
    rather than always a circle, for collision check.
Obstacles are circles with radius. 
"""

class Config:
    """
    simulation parameter class
    """

    def __init__(self):
        # robot parameter
        self.max_speed = 1.0  # [m/s]
        self.min_speed = 0.0  # [m/s]
        self.max_yaw_rate = 40.0 * math.pi / 180.0  # [rad/s]
        self.max_accel = 0.2  # [m/ss]
        self.max_delta_yaw_rate = 40.0 * math.pi / 180.0  # [rad/ss]
        self.v_resolution = 0.01  # [m/s]
        self.yaw_rate_resolution = 0.1 * math.pi / 180.0  # [rad/s]
        self.dt = 0.1  # [s] Time tick for motion prediction
        self.predict_time = 1.0  # [s]
        self.check_time = 100.0 # [s] Time to check for collision - a large number
        self.to_goal_cost_gain = 0.2
        self.speed_cost_gain = 1
        self.obstacle_cost_gain = 0.05
        self.robot_stuck_flag_cons = 0.001  # constant to prevent robot stucked
        self.robot_type = dwa.RobotType.rectangle
        self.catch_goal_dist = 0.5  # [m] goal radius
        self.catch_localgoal_dist = 1.0  # [m] local goal radius
        self.obstacle_radius = 0.5  # [m] for collision check

        # if robot_type == RobotType.circle
        # Also used to check if goal is reached in both types
        self.robot_radius = 0.5  # [m] for collision check

        # if robot_type == RobotType.rectangle
        self.robot_width = 0.5  # [m] for collision check
        self.robot_length = 1.2  # [m] for collision check
        self.robot_dim = self.robot_length # [m] for collision check # -Aaryan

    @property
    def robot_type(self):
        return self._robot_type

    @robot_type.setter
    def robot_type(self, value):
        if not isinstance(value, dwa.RobotType):
            raise TypeError("robot_type must be an instance of RobotType")
        self._robot_type = value


config = Config()



# Start- Wen Ci-------------------------------------------------------------------------------------------------------------------------------------------------------------

# ----- Set up the start and goal positions -----
# Set the start and goal positions
# Get start point
# Open the file and read the data
with open('start_point.txt', 'r+') as file:
    startpoint = file.read().strip()  # Read and remove any whitespace
    # Clear file
    file.seek(0)
    file.truncate()

# Convert the string data to a list
startpoint_list = eval(startpoint)
print('Start point received:', startpoint_list)

# Assign values to sx and sy
sx, sy = startpoint_list[0], startpoint_list[1]

# Get end point
# Open the file and read the data
with open('end_point.txt', 'r+') as file:
    endpoint = file.read().strip()  # Read and remove any whitespace
    # Clear file
    file.seek(0)
    file.truncate()

# Convert the string data to a list
endpoint_list = eval(endpoint)
print('End point received:', endpoint_list)

# Assign values to sx and sy
gx, gy = endpoint_list[0], endpoint_list[1]

# End- Wen Ci--------------------------------------------------------------------------------------------------------------------------------------------------------------

# Start -Aaryan
# ---- Getting starting and goal coordinates from GUI ---- 

if len(sys.argv) not in [3, 4]:  # 7 arguments for circle, 8 for rectangle
    print("Usage: python robot_controller.py start_x start_y end_x end_y [length width] OR [radius]")
    sys.exit(1)

try:
    # # Read coordinates from command-line arguments
    # sx = float(sys.argv[1])
    # sy = float(sys.argv[2])
    # gx = float(sys.argv[3])
    # gy = float(sys.argv[4])

    if len(sys.argv) == 4: # For rectangle
        config.robot_type = dwa.RobotType.rectangle
        config.robot_length = float(sys.argv[1])
        config.robot_width = float(sys.argv[2])
        selected_map = sys.argv[3]
    elif len(sys.argv) == 3: # For circle
        config.robot_type = dwa.RobotType.circle
        config.robot_radius = float(sys.argv[1])
        config.robot_dim = config.robot_radius
        selected_map = sys.argv[2]
    
except ValueError:
    print("Error: All arguments must be numbers.")
    sys.exit(1)
    
#End -Aaryan
# ----- Set up the map -----
ox, oy = [], []
# Load obstacles from the selected map file
maps_dir = os.path.join(os.path.dirname(__file__), "Maps_2")
map_file = os.path.join(maps_dir, f"{selected_map}.txt")  
print(map_file)

is_ob = 0
#map_file = f"{selected_map.lower().replace(' ', '_')}.txt"  # Convert "Map 1" to "map_1.txt"
try:
    with open(map_file, 'r') as file:
        map_code = file.read()  # Read the entire file content
        
        # Create empty lists to populate ox and oy
        ox, oy = [], []
        #ob = np.array([ox, oy]).transpose()

        # Execute the map file contents, which appends values to ox and oy
        exec(map_code)        
        # # After executing, convert ox and oy into an obstacle array
        if (is_ob == 1):
            print("Works!")
        else: 
            ob = np.array([ox, oy]).transpose()
            #print("ob", ob)
            #print("Type of ob", type(ob))
            #print("Length of ob", len(ob))

except FileNotFoundError:
    print(f"Error: Map file '{map_file}' not found.")
    sys.exit(1)
except Exception as e:
    print(f"Error: Unable to execute the map file '{map_file}'. Reason: {str(e)}")
    sys.exit(1)

# Plot the map
if show_animation:  # pragma: no cover
    plt.figure(figsize=(6, 6))
    if(os.path.basename(map_file)=="NY.txt"):
        background_img = cv2.imread("Images/NY.png", cv2.IMREAD_COLOR)  # Load as color image
        plt.imshow(cv2.cvtColor(background_img, cv2.COLOR_BGR2RGB), extent=[0, 60, 0, 60]) # Loading background image
    elif(os.path.basename(map_file)=="SG.txt"):
        background_img = cv2.imread("Images/SG.png", cv2.IMREAD_COLOR)  # Load as color image
        plt.imshow(cv2.cvtColor(background_img, cv2.COLOR_BGR2RGB), extent=[0, 60, 0, 60]) # Loading background image
    if save_animation_to_figs:
        cur_dir = os.path.dirname(__file__)
        fig_dir = os.path.join(cur_dir, 'figs')
        #os.makedirs(fig_dir, exist_ok=False)
        os.makedirs(fig_dir, exist_ok=True)
        i_fig = 0
        fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))
    # plt.plot(ox, oy, ".k")
    for (x, y) in ob:
        if(os.path.basename(map_file)!="NY.txt" and os.path.basename(map_file)!="SG.txt"):
        #     circle = plt.Circle((x, y), config.obstacle_radius, color="black", alpha=0) #alpha = 0 makes the plots transparent
        # elif(os.path.basename(map_file)=="SG.txt"):
        #     circle = plt.Circle((x, y), config.obstacle_radius, color="black", alpha=0.5) #alpha = 0 makes the plots transparent
        #else: 
            circle = plt.Circle((x, y), config.obstacle_radius, color="k") #Aaryan - changed config.robot_radius to config.obstacle_radius
            plt.gca().add_patch(circle)
    plt.plot(sx, sy, "og") #Start coord
    plt.plot(gx, gy, "*b") #Goal coord
    plt.grid(True)
    plt.axis("equal")

# ----- Run A* path planning -----
a_star_planner = a_star.AStarPlanner(
    ob, resolution=5.0, rr=1.0,
    min_x=min(*ox, sx-2, gx-2), min_y=min(*oy, sy-2, gy-2),
    max_x=max(*ox, sx+2, gx+2), max_y=max(*oy, sy+2, gy+2)
)
rx, ry = a_star_planner.planning(sx, sy, gx, gy)

# Start- Wen Ci----------------------------------------------------------------------------------------------------------------------
# To plot a line for global path
rx = rx[1:-1]  # Remove the first and last element from rx
ry = ry[1:-1]  # Remove the first and last element from ry

# Combine the start coordinates, rx and ry, and goal coordinates
x_all = [gx] + rx + [sx]  # Start, then all rx, and then goal
y_all = [gy] + ry + [sy]  # Start, then all ry, and then goal
# End- Wen Ci------------------------------------------------------------------------------------------------------------------------

road_map = np.array([x_all, y_all]).transpose()[::-1]
# print(road_map)

# Plot the path
if show_animation:  # pragma: no cover
    # plt.plot(rx, ry, "-r")
    plt.plot(rx, ry, "xb")
    plt.plot(x_all, y_all, "b-")
    #plt.pause(0.1)
    time.sleep(0.001)
    
    plt.grid(False)

    if save_animation_to_figs:
        
        plt.axis('off')
        #plt.savefig(fig_path)

        plt.savefig(fig_path, dpi=150, bbox_inches='tight',  pad_inches=0.1) #We can expriment if higher dpi works with a more powerful PC - need to change for both savefig lines
        i_fig += 1
        fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))

# # ----- Put new obstacles on the A* path -----
# new_ob = np.array([
#     [12.5, 12.5], 
#     [15.0, 17.5], 
#     [15.0, 22.5], 
#     [15.0, 27.5], 
#     [15.0, 32.5], 
#     [15.0, 37.5], 
#     [17.5, 42.5], 
#     [22.5, 42.5], 
#     [27.5, 37.5], 
#     [32.5, 32.5], 
#     [35.0, 27.5], 
#     [35.0, 22.5], 
#     [37.5, 17.5], 
#     [42.5, 17.5], 
#     [45.0, 22.5], 
#     [45.0, 27.5], 
#     [45.0, 32.5], 
#     [45.0, 37.5], 
#     [45.0, 42.5], 
#     [47.5, 47.5]
# ])
# new_ob1 = new_ob + np.array([0.5, 0.5])
# new_ob2 = new_ob + np.array([-0.5, -0.5])
# new_ob3 = new_ob + np.array([0.5, -0.5])
# new_ob4 = new_ob + np.array([-0.5, 0.5])
# new_ob = np.concatenate((new_ob1, new_ob2, new_ob3, new_ob4), axis=0)
# ob = np.append(ob, new_ob, axis=0)
# if show_animation:  # pragma: no cover
#     # plt.plot(new_ob[:,0], new_ob[:,1], ".k")
#     for (x, y) in new_ob:
#         circle = plt.Circle((x, y), config.obstacle_radius, color="k") #Changed robot_radius to obstacle_radius
#         plt.gca().add_patch(circle)

# Start- Wen Ci-----------------------------------------------------------------------------------------------------------------------------------------
# Read local obstacles from file
def read_new_obstacles():
    new_ob_list = []
    with open('local_obstacles.txt', 'w+') as pipe:
        while True:
            time.sleep(0.5)
            data = pipe.readline().strip()

            if data == 'resume':
                # Clear the file
                pipe.seek(0)
                pipe.truncate()
                break

            if data.startswith('[') and data.endswith(']'):
                array = eval(data)
                new_ob_list.append(array)
                print("Local obstacle received:", data)
        


    if new_ob_list:
        return np.array(new_ob_list)
    else:
        return np.array([])  # Return an empty array if no new obstacles

# Update plot
def update_plot_with_new_obstacles(new_obstacles):
    for (x, y) in new_obstacles:
        circle = plt.Circle((x, y), config.obstacle_radius, color="k", edgecolor="k")
        plt.gca().add_patch(circle)
    
    plt.draw()

# Continuously read new obstacles from transition.txt
while True:
    new_ob = read_new_obstacles()
    if new_ob.size > 0:
        # Append new obstacles to the current obstacle array
        ob = np.vstack((ob, new_ob))  # Combine old and new obstacles
        update_plot_with_new_obstacles(new_ob)  # Plot the new obstacles

    time.sleep(0.001)  # Allow time for the plot to refresh

    if new_ob.size > 0:
        break

print('Local obstacles plotted!')

# End- Wen Ci-------------------------------------------------------------------------------------------------------------------------------------------

# ----- Run DWA path planning -----
x = np.array([sx, sy, math.pi / 8.0, 1.0, 0.0])
# config = Config()

print(__file__ + " start!!")
trajectory = np.array(x)

#Function to write the loca distances, global distances and coordinates to text file
def write_data_to_file(filename, global_distance, local_distance, coordinates):
    with open(filename, "w") as file:
        file.write(f"Distance to Global Goal: {global_distance:.2f}\n")
        file.write(f"Distance to Local Goal: {local_distance:.2f}\n")
        file.write(f"X Coordinate: {float(coordinates[0])}\nY Coordinate: {float(coordinates[1])}\n")
                    


# def plot_dist_to_goal(ax, x, dist_to_goal): # Gives the distance from the robot to the goal
#     """ Plot the distance to the goal on the given axes. """
#     # Remove previous distance annotations if they exist
#     for annotation in ax.texts:
#         annotation.remove()

#     # Plot new distance annotation
#     ax.text( #Distance from local goal
#         x[0], x[1], f"Dist: {dist_to_goal:.2f}",
#         color='red', fontsize=8,
#         verticalalignment='bottom', horizontalalignment='right'
#     )
#     ax.text( #Distance from global goal
#     gx, gy, f"Dist: {global_dist_to_goal:.2f}",
#         color='green', fontsize=8,
#         verticalalignment='bottom', horizontalalignment='right'
#     )
#     global_dist_to_goal



if show_animation:  # pragma: no cover
    # for stopping simulation with the esc key.
    plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])
    plt_elements = []

min_obstacle_localgoal_distance = 2.0

for i_goal, dwagoal in enumerate(road_map):
    if i_goal == 0:  # Skip the start point
        continue

# Start- Wen Ci------------------------------------------------------------------------------------------------------------------------------------------
    # Check if the local goal is too close to any added obstacles  
    skip_goal = False
    for (obstacle_x, obstacle_y) in ob:
        distance_to_obstacle = math.hypot(dwagoal[0] - obstacle_x, dwagoal[1] - obstacle_y)
        if distance_to_obstacle < min_obstacle_localgoal_distance:
            skip_goal = True
            print(f"Skipping local goal {dwagoal} due to nearby obstacle at ({obstacle_x}, {obstacle_y})")
            break

    if skip_goal:
        continue  # Skip to the next local goal

# End- Wen Ci--------------------------------------------------------------------------------------------------------------------------------------------

    while True:
        u, predicted_trajectory = dwa.dwa_control(x, config, dwagoal, ob)
        x = dwa.motion(x, u, config.dt)  # simulate robot
        trajectory = np.vstack((trajectory, x))  # store state history

        if show_animation:  # pragma: no cover
            for ele in plt_elements:
                ele.remove()
            plt_elements = []
            plt_elements.append(plt.plot(predicted_trajectory[:, 0], predicted_trajectory[:, 1], "-g")[0])
            plt_elements.append(plt.plot(x[0], x[1], "xr")[0])
            plt_elements.extend(dwa.plot_robot(x[0], x[1], x[2], config)) #x[0] is x coord, x[1] is y coord
            plt_elements.extend(dwa.plot_arrow(x[0], x[1], x[2]))
            plt_elements.append(plt.plot(trajectory[:, 0], trajectory[:, 1], "-r")[0])
            #plt.pause(0.1)
            time.sleep(0.001)
            
            plt.grid(False)

            if save_animation_to_figs:
                plt.axis('off')
                #plt.savefig(fig_path)
                plt.savefig(fig_path, dpi=150, bbox_inches='tight',  pad_inches=0.1)
                i_fig += 1
                fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))

        # check reaching goal
        dist_to_goal = math.hypot(x[0] - dwagoal[0], x[1] - dwagoal[1]) # Local Goal

        global_dist_to_goal = math.hypot(x[0] - gx, x[1] - gy) # Global Goal

        current_coordinates = (x[0], x[1])

        #Write Local distance, Global Distance, and coordinates to txt file
        write_data_to_file("sensor_data.txt",global_dist_to_goal,dist_to_goal,current_coordinates)
                
        # plot_dist_to_goal(plt.gca(), x, dist_to_goal) # -Aaryan
        if i_goal == len(road_map) - 1:
            if dist_to_goal <= config.catch_goal_dist:
                print("Goal!!")
                break
        else:
            if dist_to_goal <= config.catch_localgoal_dist:
                print("Local goal!!")
                print("Distance to the goal: ", dist_to_goal)
                break
    
print("Done")
if show_animation:  # pragma: no cover
    plt.show()
        