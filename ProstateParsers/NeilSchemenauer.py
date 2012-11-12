import sys
import re

date_pat = re.compile(r'\s*\d+/\d+/\d+', re.M)
acc_number_pat = re.compile(r'S[\d-]+')
patient_pat = re.compile(r'[\d/-]+')
gleason_pat = re.compile(r'gleason\s+(score|grade\s*)?([\d\s]+)', re.I | re.M)
score_pat = re.compile(r'(\d+)\s+(\d+)\s+(\d+)')
score2_pat = re.compile(r'(\d+)\s+(\d+)')

def chunk_file(fp):
    # split file input chunks based on indentation, each chunk starts with
    # text in the leftmost column
    chunk = []
    for line in fp:
        if not line.strip():
            continue
        if line[:1] in ' \t':
            chunk.append(line)
        else:
            if chunk:
                yield ''.join(chunk)
            chunk = [line]
    if chunk:
        yield ''.join(chunk)


class ParseError(Exception):
    pass


def error(msg, text):
    sys.stdout.write('error: %s\n' % msg)
    for line in text.split('\n'):
        sys.stdout.write('    ' + line + '\n')


def parse_chunk(text):
    cases = []
    m = date_pat.match(text)
    if not m:
        raise ParseError('date')
    date = m.group(0)
    rest = text[m.end(0):].strip()
    m = acc_number_pat.match(rest)
    if not m:
        raise ParseError('acc number')
    acc_number = m.group(0)
    rest = rest[m.end(0):].strip()
    m = patient_pat.match(rest)
    if not m:
        raise ParseError('patient number')
    patient = m.group(0)
    rest = rest[m.end(0):].strip()
    block = 0
    # replace "noise" characters with spaces
    s = re.sub(r'[-=+:\[\]\(\)]', ' ', rest)
    for gm in gleason_pat.finditer(s):
        gleason = gm.group(0)
        #print 'gleason', `gleason`
        total = None # not found
        for m in score_pat.finditer(gleason):
            n1, n2, n3 = [int(n) for n in  m.groups()]
            if n1 == n2 + n3:
                total = n1
                primary = n2
                secondary = n3
                break
            elif n1 + n2 == n3:
                primary = n1
                secondary = n2
                total = n3
                break
        if total is None:
            # maybe "total" is missing, check for two numbers
            for m in score2_pat.finditer(gleason):
                primary, secondary = [int(n) for n in m.groups()]
                total = primary + secondary
        if total is not None:
            block += 1
            cases.append([date, acc_number, block, patient, primary,
                              secondary, total])
    if not cases:
        raise ParseError('gleason')
    return cases

def parse(in_fp, out_fp):
    for text in chunk_file(in_fp):
        #print 'chunk', `text`
        try:
            for row in parse_chunk(text):
                fields = ['%s' % field for field in row]
                out_fp.write(','.join(fields) + '\n')
        except ParseError, exc:
            error(str(exc), text)


def main():
    with open('dataOut.txt', 'w') as out_fp:
        with open('dataIn.txt', 'r') as in_fp:
            parse(in_fp, out_fp)


if __name__ == '__main__':
    main()
