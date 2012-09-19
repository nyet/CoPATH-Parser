from pyparsing import *

#Read the input data
filename = "dataIn.txt"
FIN      = open(filename)
TEXT     = FIN.read()

#Define a simple grammar
num = Word(nums)
accessionDate = Combine(num + "/" + num + "/" + num)("accDate")
accessionNumber = Combine("S" + num + "-" + num)("accNum")
patMedicalRecordNum = Combine(num + "/" + num + "-" + num + "-" + num)("patientNum")
gleason = Group("GLEASON" + Optional("SCORE:") + num("left") + "+" + num("right") + "=" + num("total"))
# assert 'GLEASON 5+4=9' == gleason
# assert 'GLEASON SCORE:  3 + 3 = 6' == gleason

patientData = Group(accessionDate + accessionNumber + patMedicalRecordNum)
# assert '01/02/11  S11-4444 20/111-22-3333' == patientData

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
        FOUT.write( "{0.accDate},{0.accNum},{0.patientNum},Gleason({1.left}+{1.right}={1.total})\n".format(
                        lastPatientData.patientData, match.gleason
                        ))
FOUT.close()
