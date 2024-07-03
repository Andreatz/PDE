import subprocess
import threading
from queue import Queue

from utils import out_format
from pdf2iupac import pdf2iupac_conversion
from utils.pdfimg2smiles import pdfimg2smiles_conversion
from utils.pdf2activity import pdf2activity_conversion
from utils.structure_activity import structure_activity_association
from utils.out_format import sdf_output_format
from utils.out_format import smi_output_format


def run_script(script, args):
    try:
        result = subprocess.run(['python', script, *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e.stderr.decode('utf-8')}")
        return None

def run_script_in_thread(script, args, output_queue):
    output = run_script(script, args)
    output_queue.put(output)

def process_file(file_path, start_num, end_num, output_format):
    output_queue = Queue()
    
    threads = []
    for script in [pdf2iupac_conversion, pdfimg2smiles_conversion, pdf2activity_conversion]:
        thread = threading.Thread(target=run_script_in_thread, args=(script, [file_path, str(start_num), str(end_num)], output_queue))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

    outputs = [output_queue.get() for _ in range(3)]

    if all(outputs):
        output = run_script(structure_activity_association(), outputs)
        
        if output_format == 'smi':
            smi_output_format(output)
        elif output_format == 'sdf':
            sdf_output_format(output)
        else:
            pass

def worker(queue):
    while not queue.empty():
        file_path, start_num, end_num, output_format = queue.get()
        process_file(file_path, start_num, end_num, output_format)
        queue.task_done()

def parse_range(range_str):
    try:
        if ":" in range_str:
            start_num, end_num = map(int, range_str.split(':'))
        else:
            start_num = 1
            end_num = None
        return start_num, end_num
    except ValueError:
        raise argparse.ArgumentTypeError("Range must be in the format start:end")

def main(file_path, range_str, output_format, text_file=None, threads=1):
    if range_str is None:
        start_num = 1
        end_num = None
    else:
        start_num, end_num = parse_range(range_str)
    
    if text_file:
        with open(text_file, 'r') as f:
            file_paths = [line.strip() for line in f if line.strip()]
    else:
        file_paths = [file_path]

    queue = Queue()
    for path in file_paths:
        queue.put((path, start_num, end_num, output_format))

    for _ in range(threads):
        threading.Thread(target=worker, args=(queue,), daemon=True).start()

    queue.join()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="BREVE DESCRIZIONE DEL TOOL")
    parser.add_argument("-f", "--file_path", required=True, help="Path to the file to be processed.")
    parser.add_argument("-r", "--range", help="Range in the format start:end. Use '--all' to analyze the entire file.")
    parser.add_argument("-t", "--text_file", help="Text file with a list of file paths to process.")
    parser.add_argument("-n", "--threads", type=int, default=1, help="Number of threads to be used to parallelize the process. Default = 1")
    parser.add_argument("-o", "--output_format", choices=['default', 'smi', 'sdf'], default='default', help="Output format. Default is the default format from script4. 'smi' and 'sdf' trigger additional processing scripts.")
    
    args = parser.parse_args()

    if args.range is None:
        parser.error("Argument -r/--range is required.")

    if args.range == "all":
        args.range = None

    main(args.file_path, args.range, args.output_format, args.text_file, args.threads)
