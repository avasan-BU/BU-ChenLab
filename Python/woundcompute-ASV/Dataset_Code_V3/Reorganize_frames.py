import os
import matplotlib.pyplot as plt

# Config:
tissue_dir = 'C:\\Working Folder\\20240913_R7P2_Viability2\\Sorted\\tissue_ai1'
result_grid_filename = 'C:\\Working Folder\\20240913_R7P2_Viability2\\Sorted\\viz'
grid_size_x = 12
grid_size_y = 5
result_figsize_resolution_x = grid_size_x*640/100 # 1 = 100px
result_figsize_resolution_y = grid_size_y*480/100
tissue_list = os.listdir(tissue_dir)
tissue_count = len(tissue_list)


tissue_list_subdir = [os.path.join(tissue_dir, loc, 'segment_ph1', 'visualizations') for loc in tissue_list if not loc.endswith('Drift')]


for subdir in tissue_list_subdir:
    if not subdir.endswith('Drift'):
        image_list = []
        for file in os.listdir(subdir):
            if file.casefold().endswith('.png'):
                image_list.append(os.path.join(subdir, file))
        images_count = len(image_list)
        # Calculate the grid size:
        # Create plt plot:
        fig, axes = plt.subplots(grid_size_y, grid_size_x, figsize=(result_figsize_resolution_x, result_figsize_resolution_y))

        for current_file_number, image_filename in enumerate(image_list):
            x_position = current_file_number % grid_size_x
            y_position = current_file_number // grid_size_x

            plt_image = plt.imread(image_list[current_file_number])
            axes[y_position, x_position].imshow(plt_image)
            print(current_file_number, '/', images_count, ': ', image_filename)

        plt.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)
        plt.savefig(os.path.join(result_grid_filename, subdir.split('\\')[-3]+'.png'))


