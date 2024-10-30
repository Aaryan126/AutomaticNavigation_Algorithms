import os, sys

rpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(rpath)

import a_star
import dynamic_window_approach_paper as dwa

import math
import numpy as np
import matplotlib.pyplot as plt

show_animation = True
save_animation_to_figs = False

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
    """ simulation parameter class """

    def __init__(self):
        self.max_speed = 2.0  # [m/s]
        self.min_speed = 0.0  # [m/s]
        self.max_yaw_rate = 40.0 * math.pi / 180.0  # [rad/s]
        self.max_accel = 0.2  # [m/ss]
        self.max_delta_yaw_rate = 40.0 * math.pi / 180.0  # [rad/ss]
        self.v_resolution = 0.01  # [m/s]
        self.yaw_rate_resolution = 0.1 * math.pi / 180.0  # [rad/s]
        self.dt = 0.1  # [s] Time tick for motion prediction
        self.predict_time = 1.0  # [s]
        self.check_time = 100.0  # [s] Time to check for collision - a large number
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

    @property
    def robot_type(self):
        return self._robot_type

    @robot_type.setter
    def robot_type(self, value):
        if not isinstance(value, dwa.RobotType):
            raise TypeError("robot_type must be an instance of RobotType")
        self._robot_type = value

config = Config()

# ----- Set up the map -----
ox, oy = [], []

#Border
for i in range(60):
    ox.append(i)
    oy.append(0.0)
for i in range(60):
    ox.append(60.0)
    oy.append(i)
for i in range(61):
    ox.append(i)
    oy.append(60.0)
for i in range(61):
    ox.append(0.0)
    oy.append(i)

# Inner Walls
# Vertical
for i in range(46):
    ox.append(30.0)
    oy.append(i)
for i in range(46):
    ox.append(45.0)
    oy.append(15.0 + i)

# Horizontal
for i in range(15):
    ox.append(1.0 + i)
    oy.append(15.0)
for i in range(15):
    ox.append(15.0 + i)
    oy.append(30.0)
for i in range(15):
    ox.append(1.0 + i)
    oy.append(45.0)

ob = np.array([ox, oy]).transpose()
# ----- Set up the map -----
ob1 = [20,20]


# ----- Set up the start and goal positions -----
sx, sy = 10.0, 10.0  # Start position
gx, gy = 50.0, 50.0  # Initial goal position

# Function to update the goal position dynamically
def update_goal(event):
    global gx, gy, sx, sy, a_star_planner, ob
    if event.button == 1:  # Left-click to update start position
        sx, sy = event.xdata, event.ydata
        print(f"New start position: ({sx}, {sy})")

    elif event.button == 3:  # Right-click to update goal position
        gx, gy = event.xdata, event.ydata
        print(f"New goal position: ({gx}, {gy})")
    
    plt.gca().cla()  # Clear current plot
    plot_map()  # Replot map with new goal

    #Run A* path planning with update start and end goal 
    rx, ry = a_star_planner.planning(sx, sy, gx, gy)
    road_map = np.array([rx, ry]).transpose()[::-1]

    plt.plot(rx, ry, "xb") #Plot A* path
    plt.plot(sx, sy, "og") #Start position
    plt.plot(gx, gy, "*b") #Goal position
    plt.draw()


# Plot the obstacles and start/goal points
def plot_map():
    plt.grid(True)
    plt.axis("equal")
    circlee = plt.Circle((ob1[0],ob1[1]), config.robot_radius, color="k")
    plt.gca().add_patch(circlee)
    for (x, y) in ob:
        circle = plt.Circle((x, y), config.robot_radius, color="k")
        plt.gca().add_patch(circle)



# Plot the map and set up dynamic goal updating
if show_animation:
    if save_animation_to_figs:
        cur_dir = os.path.dirname(__file__)
        fig_dir = os.path.join(cur_dir, 'figs')
        os.makedirs(fig_dir, exist_ok=False)
        i_fig = 0
        fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))
    # plt.plot(ox, oy, ".k")
    plot_map()
    plt.plot(sx, sy, "og")
    plt.plot(gx, gy, "*b")
    plt.gcf().canvas.mpl_connect('button_press_event', update_goal)
    plt.title(
        "Dynamic Obstacles Turned On. Left-click to set new goal. Right-click to set new goal.\n"
        "Middle click to add obstacles.Press Enter to start DWA",
        fontsize=10
    )    
# ----- Run A* path planning -----
a_star_planner = a_star.AStarPlanner(
    ob, resolution=5.0, rr=1.0,
    min_x=min(*ox, sx-2, gx-2), min_y=min(*oy, sy-2, gy-2),
    max_x=max(*ox, sx+2, gx+2), max_y=max(*oy, sy+2, gy+2)
)

# Function to add obstacles
def on_click(event):
    
    if event.button == 2:  # Left click
        if event.xdata is not None and event.ydata is not None:
            # Add new obstacle to the list
            ob = np.append(ob, [[event.xdata, event.ydata]], axis=0)
            circle = plt.Circle((event.xdata, event.ydata), config.robot_radius, color="k")
            plt.gca().add_patch(circle)
            plt.draw()
            plt.pause(0.001)

# Function to start DWA on Enter key press
def on_key(event):
    if event.key == 'enter':
        plt.close()  # Close the current plot

if show_animation:
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    plt.gcf().canvas.mpl_connect('key_press_event', on_key)

plt.show()
# # ----- Put new obstacles on the A* path -----
# new_ob = np.array([
#     [15.0, 10.0],
#     [20.0, 15.0],
#     [20.0, 20.0],
#     [15.0, 25.0],
#     [10.0, 30.0],
#     [15.0, 35.0],
#     [20.0, 40.0],
#     [25.0, 45.0],
#     [30.0, 50.0],
#     [35.0, 45.0],
#     [35.0, 40.0],
#     [35.0, 35.0],
#     [35.0, 30.0],
#     [35.0, 25.0],
#     [35.0, 20.0],
#     [40.0, 15.0],
#     [45.0, 10.0],
#     [50.0, 15.0],
#     [50.0, 20.0],
#     [50.0, 25.0],
#     [50.0, 30.0],
#     [50.0, 35.0],
#     [50.0, 40.0],
#     [50.0, 45.0],
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
#         circle = plt.Circle((x, y), config.robot_radius, color="k")
#         plt.gca().add_patch(circle)

# Reset plot limits before starting DWA
plt.figure()
plt.grid(True)
plt.axis("equal")
plt.title("Path Planning After Adding Obstacles and updated Goals")

# ----- Plotting the updated path once goal is changed -----
rx, ry = a_star_planner.planning(sx, sy, gx, gy)
road_map = np.array([rx, ry]).transpose()[::-1]

# Plot the path
if show_animation:  # pragma: no cover
    # plt.plot(rx, ry, "-r")
    plt.plot(rx, ry, "xb")
    plt.pause(0.001)

    if save_animation_to_figs:
        plt.savefig(fig_path)
        i_fig += 1
        fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))


# Run the DWA with the updated goal
x = np.array([sx, sy, math.pi / 8.0, 1.0, 0.0])
#config = Config()

print(__file__ + " start!!")
trajectory = np.array(x)

if show_animation: # pragma: no cover
    # for stopping simulation with the esc key.
    plt.gcf().canvas.mpl_connect(
        'key_release_event',
        lambda event: [exit(0) if event.key == 'escape' else None])
    plt_elements = []
    dyn_ob = []
    plt.figure()
    plt.grid(True)
    plt.axis("equal")
    plot_map()
    plt.plot(sx, sy, "og")
    plt.plot(gx, gy, "*b")
    plt_elements=[]
    plt.plot(rx, ry, "xb") #Plot A* path
    plt.pause(0.001)

min_obstacle_localgoal_distance = 2.0

for i_goal, dwagoal in enumerate(road_map):
    if i_goal == 0:  # Skip the start point
        continue

    # Check if the local goal is too close to any added obstacles  
    skip_goal = False
    for (obstacle_x, obstacle_y) in ob:
        distance_to_obstacle = math.hypot(dwagoal[0] - obstacle_x, dwagoal[1] - obstacle_y)
        if distance_to_obstacle <= min_obstacle_localgoal_distance:
            skip_goal = True
            print(f"Skipping local goal {dwagoal} due to nearby obstacle at ({obstacle_x}, {obstacle_y})")
            break

    if skip_goal:
        continue  # Skip to the next local goal

    while True:
        u, predicted_trajectory = dwa.dwa_control(x, config, dwagoal, ob)
        x = dwa.motion(x, u, config.dt)  # Simulate robot motion
        trajectory = np.vstack((trajectory, x))  # Store state history

        if show_animation: #pragma: no cover
            for ele in plt_elements:
                ele.remove()
            plt_elements = []
            plt_elements.append(plt.plot(predicted_trajectory[:, 0], predicted_trajectory[:, 1], "-g")[0])
            plt_elements.append(plt.plot(x[0], x[1], "xr")[0])
            plt_elements.extend(dwa.plot_robot(x[0], x[1], x[2], config))
            plt_elements.extend(dwa.plot_arrow(x[0], x[1], x[2]))
            plt_elements.append(plt.plot(trajectory[:, 0], trajectory[:, 1], "-r")[0])

            if ob1[0]<30 or ob1[1]<30:
                ob1[0],ob1[1] =ob1[0]+0.01,ob1[1]+0.01
                print(ob1)
                plt_elements.append(plt.plot(ob1[0],ob1[1], "xr")[0])
                plt.pause(0.001)
                if save_animation_to_figs:
                    plt.savefig(fig_path)
                    i_fig += 1
                    fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))

            else:
                if save_animation_to_figs:
                    plt.savefig(fig_path)
                    i_fig += 1
                    fig_path = os.path.join(fig_dir, 'frame_{}.png'.format(i_fig))

        # Check if the goal or local goal is reached
        dist_to_goal = math.hypot(x[0] - dwagoal[0], x[1] - dwagoal[1])
        if i_goal == len(road_map) - 1:
            if dist_to_goal <= config.catch_goal_dist:
                print("Goal!!")
                break
        else:
            if dist_to_goal <= config.catch_localgoal_dist:
                print("Local goal!!")
                break

print("Done")
if show_animation: #pragma: no cover
    plt.show()
