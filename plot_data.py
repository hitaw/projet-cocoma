import os
import matplotlib.pyplot as plt

def plot_data(folder_path, method=None, heuristic=None, ordonnancement=None):
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    all_mean_data = []
    all_execution_time = []
    all_legend = []
    
    for file_path in files:
        with open(file_path, "r") as file:
            data = file.readlines()

        # First line is the title
        title = data[0].strip()
        file_method = title.split(",")[0].split(":")[-1].strip()
        file_heuristic = title.split(",")[1].split(":")[-1].strip()
        file_ordonnancement = title.split(",")[2].split(":")[-1].strip()

        # Filter based on method, heuristic, and ordonnancement
        if (method and file_method != method) or (heuristic and file_heuristic != heuristic) or (ordonnancement and file_ordonnancement != ordonnancement):
            continue

        all_legend.append(f"{file_method}, {file_heuristic}, {file_ordonnancement}")        
        data = data[1:]

        # Second line is basically the header
        header = data[0].strip().split(",")
        data = data[1:]

        data_list_by_run = []
        execution_time = []
        for line in data:
            if "Run" in line:
                data_list_by_run.append({key: [] for key in header})
                continue
            if "Execution time" in line:
                execution_time.append(float(line.split(":")[-1].strip()))
                continue
            line = line.strip().split(",")
            for i, value in enumerate(line):
                data_list_by_run[-1][header[i]].append(int(value))

        # Doing mean of all runs
        mean_data = {key: [] for key in header}
        for run in data_list_by_run:
            # We sort the taxis by number of tasks
            taxis = sorted(run[" Number of tasks completed"], reverse=True)
            for i, taxi in enumerate(taxis):
                for key in header:
                    if i == len(mean_data[key]):
                        mean_data[key].append(0)
                    mean_data[key][i] += run[key][i]

        for key in header:
            mean_data[key] = [value / len(data_list_by_run) for value in mean_data[key]]

        # Sort mean_data by " Number of tasks completed" in descending order
        sorted_indices = sorted(range(len(mean_data[" Number of tasks completed"])), key=lambda k: mean_data[" Number of tasks completed"][k], reverse=True)
        for key in header:
            mean_data[key] = [mean_data[key][i] for i in sorted_indices]

        all_mean_data.append(mean_data)
        all_execution_time.append(sum(execution_time) / len(execution_time))

    # Plotting Number of tasks completed as histogram for all files
    plt.figure()
    for i, mean_data in enumerate(all_mean_data):
        label = all_legend[i]
        plt.bar([x + i * 0.2 for x in range(len(mean_data[" Number of tasks completed"]))], mean_data[" Number of tasks completed"], width=0.2, label=label)
    plt.title("Number of tasks completed")
    plt.ylabel("Number of tasks")
    plt.xlabel("Taxi")
    plt.legend()
    plt.show()

    # Plotting Total cost as histogram for all files
    plt.figure()
    for i, mean_data in enumerate(all_mean_data):
        label = all_legend[i]
        plt.bar([x + i * 0.2 for x in range(len(mean_data[" Total cost"]))], mean_data[" Total cost"], width=0.2, label=label)
    plt.title("Total cost of tasks")
    plt.ylabel("Cost")
    plt.xlabel("Taxi")
    plt.legend()
    plt.show()

    # Execution time
    
    plt.figure()
    plt.bar(all_legend, all_execution_time)
    plt.title("Execution time")
    plt.ylabel("Time (s)")
    plt.xlabel("Configuration")
    plt.show()

    # Plot total cost of tasks as a single bar for each configuration
    plt.figure()
    total_costs = [sum(mean_data[" Total cost"]) for mean_data in all_mean_data]
    plt.bar(all_legend, total_costs)
    plt.title("Total cost of tasks")
    plt.ylabel("Total Cost")
    plt.xlabel("Configuration")
    plt.show()

    # Plot pie charts for each configuration
    for i, mean_data in enumerate(all_mean_data):
        plt.figure()
        plt.pie(mean_data[" Number of tasks completed"], labels=[f"Taxi {i}" for i in range(len(mean_data[" Number of tasks completed"]))], autopct='%1.1f%%')
        plt.title(all_legend[i])
        plt.show()

plot_data("datas/", method=None, heuristic=None, ordonnancement="Glouton")
