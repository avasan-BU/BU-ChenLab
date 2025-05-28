import os
import time
from pathlib import Path
from multiprocessing import Pool, cpu_count
import psutil
from woundcompute import image_analysis as ia


def format_timespan(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def process_subfolder(args):
    input_path, subfolder = args
    position = Path(input_path).joinpath(subfolder)
    start_time = time.time()
    try:
        time_all, action_all = ia.run_all(position)
        elapsed_time = time.time() - start_time
        return {
            "thread": os.path.basename(input_path),
            "tissue": subfolder,
            "status": "success",
            "time": format_timespan(elapsed_time),
            "details": f"Processed {len(time_all)} actions"
        }
    except Exception as ex:
        return {
            "thread": os.path.basename(input_path),
            "tissue": subfolder,
            "status": "error",
            "time": format_timespan(time.time() - start_time),
            "details": str(ex)
        }


def estimate_memory_per_process(input_path, sample_size=1):
    subfolders = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
    sample = subfolders[:sample_size] if len(subfolders) > sample_size else subfolders

    total_memory = 0
    for subfolder in sample:
        print(subfolder)
        process = psutil.Process()
        print(process)
        mem_before = process.memory_info().rss
        print(mem_before)
        process_subfolder((input_path, subfolder))
        mem_after = process.memory_info().rss
        total_memory += (mem_after - mem_before)

    return total_memory // len(sample) if sample else 500 * 1024 * 1024  # Default to 500MB if no sample


def process_basename(basename, path_output):
    input_path = os.path.join(path_output, basename)
    subfolders = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
    print(subfolders)
    if not subfolders:
        print(f"No subfolders found in {input_path}. Skipping this basename.")
        return

    print(f"Starting wound compute for {basename}...")
    print("Start time:", time.ctime())

    # Estimate memory per process
    memory_per_process = estimate_memory_per_process(input_path)
    print(memory_per_process)
    # Determine the number of processes based on CPU cores and available memory
    num_cores = cpu_count()
    print(num_cores)
    available_memory = psutil.virtual_memory().available
    print(available_memory)
    num_processes = min(num_cores, max(1, int(available_memory / memory_per_process)))

    print(f"Estimated memory per process: {memory_per_process / (1024 * 1024):.2f} MB")
    print(f"Number of processes: {num_processes}")

    with Pool(processes=num_processes) as pool:
        results = pool.map(process_subfolder, [(input_path, subfolder) for subfolder in subfolders])

    # Process and print results
    for result in results:
        if result['status'] == 'success':
            print(f"Thread: {result['thread']}, tissue: {result['tissue']}, time: {result['time']}")
        else:
            print(f"Thread: {result['thread']}, tissue: {result['tissue']}, time: {result['time']}")
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
