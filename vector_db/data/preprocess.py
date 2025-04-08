import os 
import re 

dir_path = '/home/pinto/Desktop/MLE/vector_db/data/transcripts'
raw_dataset_path = './transcripts'

transcript_paths = [os.path.join(dir_path , transcript) for transcript in os.listdir(raw_dataset_path)]

processed_dataset_path = './processed_transcripts'
print(transcript_paths[0])

def preprocess_transcripts(file_paths, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()

        # Strip numbers at the beginning of each line
        stripped_lines = [re.sub(r'^\d+\.\d+\s*', '', line) for line in lines]

        # Create output file path
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_dir, filename)

        # Write the modified content
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(stripped_lines)

        print(f"Processed: {file_path} -> {output_path}")


if __name__ == "__main__":
    preprocess_transcripts(transcript_paths, processed_dataset_path)