import os

directory = './implementation'
output_file = 'output.txt'

with open(output_file, 'w', encoding='utf-8') as outfile:
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            try:
                with open(os.path.join(directory, filename), 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read() + "\n")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
