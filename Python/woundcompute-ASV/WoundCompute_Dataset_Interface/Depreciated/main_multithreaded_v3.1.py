import os
import time
from pathlib import Path
from multiprocessing import Pool, cpu_count
import psutil
from woundcompute import image_analysis as ia


def process_subfolder(args):
    input_path, subfolder = args
    start_time = time.time()
    try:
        time_all, action_all = ia.run_all(position)
        elapsed_time = time.time() - start_time
        return {
            "thread": input_path,
            "tissue": subfolder,
            "status": "success",
            "time": elapsed_time,
            "details": f"Processed {len(time_all)} time points"
        }
    except Exception as ex:
        return {
            "thread": input_path,
            "tissue": subfolder,
            "status": "error",
            "time": time.time() - start_time,
            "details": str(ex)
        }


def measure_cpu_utilization(input_path, subfolder):
    process = psutil.Process()
    start_cpu_time = process.cpu_times().user + process.cpu_times().system
    start_time = time.time()

    process_subfolder((input_path, subfolder))

    end_cpu_time = process.cpu_times().user + process.cpu_times().system
    end_time = time.time()

    cpu_utilization = (end_cpu_time - start_cpu_time) / (end_time - start_time) * 100
    return cpu_utilization


def process_basename(basename, path_output):
    input_path = os.path.join(path_output, basename)
    subfolders = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]

    if not subfolders:
        print(f"No subfolders found in {input_path}. Skipping this basename.")
        return

    print(f"Starting wound compute for {basename}...")
    print("Start time:", time.ctime())

    # Measure CPU utilization of a single process
    print(subfolders[0])
    cpu_utilization_per_process = measure_cpu_utilization(input_path, subfolders[0])
    print(f"CPU utilization per process: {cpu_utilization_per_process:.2f}%")

    # Calculate optimal number of processes
    max_cpu_utilization = 80  # Target maximum utilization percent
    optimal_num_processes = max(1, int(max_cpu_utilization / cpu_utilization_per_process))
    optimal_num_processes = min(optimal_num_processes, cpu_count(), len(subfolders))

    print(f"Optimal number of processes: {optimal_num_processes}")

    with Pool(processes=optimal_num_processes) as pool:
        results = pool.map(process_subfolder, [(input_path, subfolder) for subfolder in subfolders])

    # Process and print results
    for result in results:
        if result['status'] == 'success':
            print(
                f"Thread: {result['thread']}, tissue: {result['tissue']}, time: {result['time']:.2f}s, {result['details']}")
        else:
            print(f"Thread: {result['thread']}, tissue: {result['tissue']}, time: {result['time']:.2f}s")
            print("---------ERROR OF SOME DESCRIPTION HAS HAPPENED-------")
            print(result['details'])
            print("------------------------------------------------------")

    print(f"All processes have finished running for {basename}")
    print("Completed! Hurray!")
    print("End time:", time.ctime())


if __name__ == "__main__":
    basename_list = ['tissue_bi']  # Your list of basenames
    path_output = "C:\\Working Folder\\multitest"  # Your output path

    for basename in basename_list:
        process_basename(basename, path_output)
