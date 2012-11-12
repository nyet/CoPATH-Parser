import re
 
file = open('/home/cristi/Documents/programare/data.txt')
data = file.read()
 
def split_blocks(data):
    pattern = "(\d\d/\d\d/\d\d)"
    return re.split(pattern, data)
   
def parse(data):
    response = []
    text = data.strip().split()
   
    case_number = text[0]
    fmp = text[1]
    block = data.count('GLEASON GRADE') + data.count('GLEASON SCORE')
 
    index = data.find('GLEASON')
    tumors = get_tumors(data[index:])
    scores = sort_tumors(tumors)
 
    return [case_number, block, fmp, scores[0], scores[1], scores[2]]
   
def get_tumors(text):
    count = 0
    result = []
    for char in text:
        if char.isdigit():
            result.append(int(char))
            count += 1
            if count == 3: return result
 
def sort_tumors(tumors):
    tumor_sum = max(tumors)
    tumors.remove(tumor_sum)
    return [tumors[0], tumors[1], tumor_sum]
 
blocks = split_blocks(data)
output = open('/home/cristi/Documents/programare/data.out', 'w')
 
for i in range(1, len(blocks), 2):
    sep = ','
    line = ''
    line += blocks[i]
    line += sep
    stuff_to_print = parse(blocks[i+1])
    for j in stuff_to_print:
        line = line + str(j) + sep
    print line
    output.write(line)
    output.write('\n')
