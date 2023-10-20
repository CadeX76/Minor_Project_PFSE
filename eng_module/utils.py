import csv

def str_to_int(s: str) -> int|str:
    '''
    Returns a integer or string
    '''
    try:
        value = int(s)
    except ValueError:
        value = s

    return value

def str_to_float(s: str) -> float|str:
    '''
    Returns a float or string
    '''
    try:
        value = float(s)
    except ValueError:
        value = s

    return value

def read_csv_file(filename: str)-> list[list[str]]:
    """
    Returns the contents of a file
    'file_name' - name of the file to be read
    """
    file_data = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for line in csv_reader:
            file_data.append(line)
    return file_data