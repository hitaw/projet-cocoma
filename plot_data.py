import os
import matplotlib.pyplot as plt

def plot_data(folder_path, method=None, heuristic=None, ordonnancement=None):
    plot_folder = "plots/"
    files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    all_mean_data = []
    all_execution_time = []
    all_legend = []

    colors = plt.cm.get_cmap('tab10', len(files)).colors  # Get a list of colors

    for file_index, file_path in enumerate(files):
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

        # Normalize total cost by the number of tasks
        mean_data[" Total cost"] = [cost / tasks if tasks != 0 else 0 for cost, tasks in zip(mean_data[" Total cost"], mean_data[" Number of tasks completed"])]

        # Calculate the ratio of tasks completed
        total_tasks = sum(mean_data[" Number of tasks completed"])
        mean_data[" Task ratio"] = [tasks / total_tasks for tasks in mean_data[" Number of tasks completed"]]

        all_mean_data.append(mean_data)
        all_execution_time.append(execution_time)

    # Ensure "Random" method is last
    if "Random" in [legend.split(",")[0] for legend in all_legend]:
        random_index = [legend.split(",")[0] for legend in all_legend].index("Random")
        all_mean_data.append(all_mean_data.pop(random_index))
        all_execution_time.append(all_execution_time.pop(random_index))
        all_legend.append(all_legend.pop(random_index))

    # Plotting Task ratio as histogram for all files
    plt.figure()
    for i, mean_data in enumerate(all_mean_data):
        label = ""
        if not method:
            label += all_legend[i].split(",")[0]
        if not heuristic:
            label += all_legend[i].split(",")[1]
        if not ordonnancement and heuristic != "Insert":
            label += all_legend[i].split(",")[2]
        plt.bar([x + i * 0.2 for x in range(len(mean_data[" Task ratio"]))], mean_data[" Task ratio"], width=0.2, label=label, color=colors[i])
    titre = "Ratio of tasks completed"
    if method:
        titre += " - Method: " + method
    if heuristic:
        titre += " - Heuristic: " + heuristic
    if ordonnancement:
        titre += " - Ordonnancement: " + ordonnancement
    plt.title(titre)
    plt.ylabel("Task ratio")
    plt.xlabel("Taxi")
    plt.xticks(range(len(mean_data[" Task ratio"])))  # Set x-axis to 0, 1, 2, etc.
    plt.legend()
    name = plot_folder+"task_ratio_"+str(method)+"_"+str(heuristic)+"_"+str(ordonnancement)+".png"
    plt.savefig(name)
    plt.close()
    #plt.show()

    # Plotting Total cost as histogram for all files
    plt.figure()
    for i, mean_data in enumerate(all_mean_data):
        label = ""
        if not method:
            label += all_legend[i].split(",")[0]
        if not heuristic:
            label += all_legend[i].split(",")[1]
        if not ordonnancement and heuristic != "Insert":
            label += all_legend[i].split(",")[2]
        plt.bar([x + i * 0.2 for x in range(len(mean_data[" Total cost"]))], mean_data[" Total cost"], width=0.2, label=label, color=colors[i])
    titre = "Total cost of tasks"
    if method:
        titre += " - Method: " + method
    if heuristic:
        titre += " - Heuristic: " + heuristic
    if ordonnancement:
        titre += " - Ordonnancement: " + ordonnancement
    plt.title(titre)
    plt.ylabel("Cost")
    plt.xlabel("Taxi")
    plt.legend()
    name = plot_folder+"total_cost_"+str(method)+"_"+str(heuristic)+"_"+str(ordonnancement)+".png"
    plt.savefig(name)
    plt.close()
    #plt.show()

    # Execution time as box plot
    plt.figure()
    labels = []
    for i, mean_data in enumerate(all_mean_data):
        lab = ""
        if not method:
            lab += all_legend[i].split(",")[0]
        if not heuristic:
            lab += all_legend[i].split(",")[1]
        if not ordonnancement and heuristic != "Insert":
            lab += all_legend[i].split(",")[2]
        labels.append(lab)
    
    plt.boxplot(all_execution_time, labels=labels)
    titre = "Execution time"
    if method:
        titre += " - Method: " + method
    if heuristic:
        titre += " - Heuristic: " + heuristic
    if ordonnancement:
        titre += " - Ordonnancement: " + ordonnancement
    plt.title(titre)
    plt.ylabel("Time (s)")
    plt.xlabel("Configuration")
    name = plot_folder+"execution_time_"+str(method)+"_"+str(heuristic)+"_"+str(ordonnancement)+".png"
    plt.savefig(name)
    plt.close()
    #plt.show()

    # Plot total cost of tasks as a single bar for each configuration
    plt.figure()
    total_costs = [sum(mean_data[" Total cost"]) for mean_data in all_mean_data]
    labels = []
    for i, mean_data in enumerate(all_mean_data):
        lab = ""
        if not method:
            lab += all_legend[i].split(",")[0]
        if not heuristic:
            lab += all_legend[i].split(",")[1]
        if not ordonnancement and heuristic != "Insert":
            lab += all_legend[i].split(",")[2]
        labels.append(lab)
    plt.bar(labels, total_costs, color=colors[:len(all_legend)])
    titre = "Average cost for one task"
    if method:
        titre += " - Method: " + method
    if heuristic:
        titre += " - Heuristic: " + heuristic
    if ordonnancement:
        titre += " - Ordonnancement: " + ordonnancement
    plt.title(titre)
    plt.ylabel("Total Cost")
    plt.xlabel("Configuration")
    name = plot_folder+"total_cost_"+str(method)+"_"+str(heuristic)+"_"+str(ordonnancement)+".png"
    plt.savefig(name)
    plt.close()
    #plt.show()

    # Plot pie charts for each configuration
    for i, mean_data in enumerate(all_mean_data):
        plt.figure()
        plt.pie(mean_data[" Number of tasks completed"], labels=[f"Taxi {i}" for i in range(len(mean_data[" Number of tasks completed"]))], autopct='%1.1f%%')
        plt.title(all_legend[i])
        name = plot_folder+"pie_chart_" + all_legend[i].replace(", ", "_").replace(" ", "_") + ".png"
        plt.savefig(name)
        plt.close()
        #plt.show()

plot_data("datas/", method="SSI", heuristic=None, ordonnancement=None)
plot_data("datas/", method="PSI", heuristic=None, ordonnancement=None)
plot_data("datas/", method="Regret", heuristic=None, ordonnancement=None)
plot_data("datas/", method="Random", heuristic=None, ordonnancement=None)
plot_data("datas/", method=None, heuristic="Prim", ordonnancement="Glouton")
plot_data("datas/", method=None, heuristic="Insert", ordonnancement=None)
