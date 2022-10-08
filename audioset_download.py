# Code Contributor - Ankit Shah - ankit.tronix@gmail.com
# Modified - Alexander Bakhtin - alexander.bakhtin@tuni.fi
import os
import sys
import argparse
from multiprocessing import Pool

#Method to download audio - Downloads the best audio available for audio id, calls the formatting audio function and then segments the audio formatted based on start and end time. 
def download_audio(segment_id, dataset_name, clip_length=10000):

    parts = segment_id.split('_')
    query_id = '_'.join(parts[:-1])

    start_seconds = int(parts[-1])//1000
    clip_length = clip_length/1000
    end_seconds = start_seconds+int(clip_length)

    url = "https://www.youtube.com/watch?v=" + query_id

    download_folder = dataset_name + "_downloaded" 
    formatted_folder = dataset_name + "_formatted"
    segmented_folder = dataset_name + "_segmented"

    path_to_download = os.path.join(download_folder, f"Y{query_id}.wav")
    path_to_formatted_audio = os.path.join(formatted_folder, f"Y{query_id}.wav")
    path_to_segmented_audio = os.path.join(segmented_folder, f"Y{segment_id}.wav")

    try:
        print(f"{query_id}: Downloading...")
        if os.path.exists(path_to_download):
            print(f"{query_id}: Downloaded file already exists.")
        else:
            cmdstring = f"yt-dlp -f 'ba' -x --audio-format wav {url} -o '{path_to_download}'"
            os.system(cmdstring)
        
        print(f"{query_id}: Formatting...")
        if os.path.exists(path_to_formatted_audio):
            print(f"{query_id}: Formatted file already exists.")
        else:
            cmdstring = f"sox {path_to_download} -G -c 1 -b 16 -r 44100 f{path_to_formatted_audio}"
            os.system(cmdstring)

        print(f"{query_id}: Trimming...")
        if os.path.exists(path_to_segmented_audio):
            print(f"{query_id}: Trimmed file already exists.")
        else:
            cmdstring = f"sox {path_to_formatted_audio} {path_to_segmented_audio} trim {start_seconds} {clip_length}"
            os.system(cmdstring)

    except Exception as ex:
        print(f"{query_id}: Error - {str(ex)}")


#Download audio - Reads 3 lines of input csv file at a time and passes them to multi_run wrapper which calls download_audio_method to download the file based on id.
#Multiprocessing module spawns 3 process in parallel which runs download_audio_method. Multiprocessing, thus allows downloading process to happen in 40 percent of the time approximately to downloading sequentially - processing line by line of input csv file. 
def parallelize_download(input_file,num_workers=None, clip_length=10000):
    dataset_name = input_file.removesuffix('.txt')
    with open(input_file, 'r) as segments_info_file:
        while True:
            lines_list = []
            last_loop = False
            for i in range(num_workers):
                line = next(segments_info_file, None)
                if line is not None: lines_list.append((line.removesuffix('\n'), dataset_name, clip_length))
                last_loop = line is None
        
            with Pool(num_workers) as P:
                P.starmap(download_audio,lines_list)
            if last_loop: break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='List of YouTube file-intervals to be downloaded in format YTID_STARTMILLISECONDS, one per line')
    parser.add_argument('--num_workers', '-n', type=int, default=None,
                        help='Amount of threads-workers to pass to Pool()')
    parser.add_argument('--clip_length', type=int, default=10000,
                        help='Length (in ms) of the clip to be extracted from the starting timestamp')
    args = parser.parse_args()
    parallelize_download(args.input,args.num_workers, args.clip_length)
