from pyparsing import Word, nums, operatorPrecedence, oneOf, opAssoc, Literal, Optional, Combine
from collections import defaultdict


num = Word(nums)


gl_parts = num("g1") + Literal('+') + num("g2")
gl_total = num("gt")

gl1 = gl_parts + Literal('=') + gl_total
gl2 = gl_total + Literal('=') + gl_parts
gl3 = gl_total + oneOf('( [') + gl_parts + oneOf(') ]')
gl4 = gl_parts + Literal("-") + gl_total
gl5 = gl_parts

gl_expr = gl1 | gl2 | gl3 | gl4 | gl5

gleason_str = "GLEASON" + Optional("SCORE") + Optional(":") + gl_expr

accessionDate = Combine(num + "/" + num + "/" + num)("accDate")
accessionNumber = Combine("S" + num + "-" + num)("accNum")
patMedicalRecordNum = Combine(num + "/" + num + "-" + num + "-" + num)("patientNum")

patientData = accessionDate + accessionNumber + patMedicalRecordNum


partMatch = patientData("patientData") | gleason_str("gleason")



blockCounter = defaultdict(lambda : 0)

def process_data(data):
    result = []
    for match in partMatch.searchString(data):
        if match.patientData:
            lpData = match
        elif match.gleason:
            if lpData is None:
                print "bad!"
                continue
            if not match.gleason.gt:
                total = str(int(match.gleason.g1) + int(match.gleason.g2))
            else:
                total = match.gleason.gt
            blockCounter[lpData.accNum] += 1
            result.append([lpData.accDate, lpData.accNum, str(blockCounter[lpData.accNum]), lpData.patientNum, match.gleason.g1, match.gleason.g2, total])
    return result




#fh = open("dataIn.txt")
fh = open("DataBig.txt")
data = fh.read()

result = process_data(data)

writer = open("Out.txt", 'w')
for row in result:
    writer.write(",".join(row) + "\n")

writer.close()

