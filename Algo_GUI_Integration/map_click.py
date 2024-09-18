import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np

# Initialize an empty list to store coordinates
coordinates = []

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_xlim([0, 10])
ax.set_ylim([0, 10])

def onclick(event):
    # Only proceed if the click happened in the plotting area
    if event.inaxes == ax:
        # Plot point and collect coordinates
        print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              (event.button, event.x, event.y, event.xdata, event.ydata))
        ax.plot(event.xdata, event.ydata, 'o', color='red')  # Plot point
        fig.canvas.draw()

        # Append the coordinates to the list
        coordinates.append([event.xdata, event.ydata])

def save_and_close(event):
    # Convert the list to a NumPy array in the required format
    new_ob = np.array(coordinates)

    # Save to a text file in the desired format
    np.savetxt('coordinates.txt', new_ob, fmt="%.1f", delimiter=", ", header="new_ob = np.array([", footer="])", comments='')

    # Close the plot window
    plt.close(fig)

# Create a button for saving coordinates and closing the window
ax_save = plt.axes([0.4, 0.01, 0.2, 0.075])
save_button = Button(ax_save, 'Save')
save_button.on_clicked(save_and_close)

# Connect the onclick function to mouse click events
cid = fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()
