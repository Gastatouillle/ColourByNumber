import matplotlib.pyplot as plt
import ast

with open("elapsedTimes.txt", "r") as file:
    contents =  ast.literal_eval(file.read())
    print(contents)
    x_coords = []
    y_coords = []
    # 1. Define your X and Y coordinates as separate lists
    for i in range(len(contents)):
        x_coords.append(contents[i][0])
        y_coords.append(contents[i][1])
    # 2. Create the line plot (marker='o' adds dots to each point)
    plt.plot(x_coords, y_coords, marker='o', color='blue', linestyle='-')

    # 3. Add styling and show the graph
    plt.title("Line Graph of XY Points")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")
    plt.grid(True)
    plt.show()