from pyparsing import *

#Read the input data
filename = "dataIn.txt"
FIN      = open(filename)
TEXT     = FIN.read()

#Define a simple grammar
num = Word(nums)
arith_expr = operatorPrecedence(num,
    [
    (oneOf('-'), 1, opAssoc.RIGHT),
    (oneOf('* /'), 2, opAssoc.LEFT),
    (oneOf('+ -'), 2, opAssoc.LEFT),
    ])
accessionDate = Combine(num + "/" + num + "/" + num)("accDate")
accessionNumber = Combine("S" + num + "-" + num)("accNum")
patMedicalRecordNum = Combine(num + "/" + num + "-" + num + "-" + num)("patientNum")
gleason = Group("GLEASON" + Optional("SCORE") + Optional("GRADE") + Optional("PATTERN") + Optional(":") + arith_expr('lhs') + Optional('=' + arith_expr('rhs')))

patientData = Group(accessionDate + accessionNumber + patMedicalRecordNum)

partMatch = patientData("patientData") | gleason("gleason")

#Open up a new file for the output
output_file = "dataOut.txt"
FOUT = open(output_file,'w')

#Parse the results
lastPatientData = None
for match in partMatch.searchString(TEXT):
    if match.patientData:
        lastPatientData = match
    elif match.gleason:
        if lastPatientData is None:
            print "bad!"
            continue
        FOUT.write( "{0.accDate},{0.accNum},{0.patientNum},{1.lhs},{1.rhs}\n".format(
                        lastPatientData.patientData, match.gleason
                        ))
FOUT.close()

# problems (test cases):
# 1) the usual case
# 2) if two gleason scores are recorded (eg, multiple tissue blocks with cancer in one case), then I need to 
#    note that, probably as a separate field
# 3) if the sum is on the left and the primary and secondary scores are on the right, then I need to move the sum
#    to the right
# 4) If someone separates the sum with a '-' instead of an '=', I need to recognize that
# 5) If score only reports a single pattern, list it as 3,nil,nil,block_number
# 6) If a tertiary pattern is noted, ignore it
# 7) If the score is formated as T (P + S) or T [P + S], handle correctly
