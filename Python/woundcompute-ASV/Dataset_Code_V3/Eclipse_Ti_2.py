import os
import shutil


basename_list_fn = ['tissue_ai']
parent_output_fn ='C:/Working Folder/Ti2/Export/s3'
parallels_in = 4
stage_pos_nd_fn =[34]
# Create processing folders
for index_fn, basename_fn in enumerate(basename_list_fn):
    path_input_fn = parent_output_fn + '/' + basename_fn
    file_list = os.listdir(path_input_fn)
    file_list.sort()

    stage_pos_max = parallels_in * int(round((len(file_list) + 1) / parallels_in)) + 1
    for p_folder in range(1, parallels_in + 1):
        loc_p_folder = path_input_fn + '/' + 'p' + f"{p_folder:02}"
        stage_pos_start = (p_folder - 1) * int(round((stage_pos_nd_fn[index_fn] + 1) / parallels_in))
        stage_pos_end = p_folder * int(round((stage_pos_nd_fn[index_fn] + 1) / parallels_in))
        if stage_pos_end > stage_pos_nd_fn[index_fn]:
            stage_pos_end = stage_pos_nd_fn[index_fn]
        try:
            os.makedirs(loc_p_folder)
            for stage_pos_fn in range(stage_pos_start, stage_pos_end):
                # define input and output paths
                move_loc_from = path_input_fn + '/' + file_list[stage_pos_fn]
                move_loc_to = loc_p_folder + '/' + file_list[stage_pos_fn]
                try:
                    shutil.move(move_loc_from, move_loc_to)
                except OSError as e:
                    # If it fails, inform the user.
                    print('Error: %s - %s.' % (e.filename, e.strerror))
        except OSError as e:
            # If it fails, inform the user.
            print('Error: %s - %s.' % (e.filename, e.strerror))

    if stage_pos_max < stage_pos_nd_fn[index_fn] + 1:
        loc_p_folder = path_input_fn + '/' + 'p' + f"{parallels_in:02}"
        for stage_pos_fn in range(stage_pos_max, stage_pos_nd_fn[index_fn] + 1):
            # define input and output paths
            move_loc_from = path_input_fn + '/' + file_list[stage_pos_fn]
            move_loc_to = loc_p_folder + '/' + file_list[stage_pos_fn]
            try:
                shutil.move(move_loc_from, move_loc_to)
            except OSError as e:
                # If it fails, inform the user.
                print('Error: %s - %s.' % (e.filename, e.strerror))