#!/usr/bin/python

import sys
import os
from SylError import SylError
from Constants import Constants
from Penalty import Penalty

if __name__ == '__main__':
  try:
    script, hypPath, refPath, reportDir, reportName, refLangSpecsPath, sclitePath = sys.argv
  except ValueError:
    print "TranslitScorer.py\thypPath\trefPath\treportDir\treportName\trefLangSpecs\tsclitePath"
    sys.exit(1)

SYL_DELIM = '.'
SUBSYL_DELIM = ' '
ONSET   = Constants.ONSET
NUCLEUS = Constants.NUCLEUS
CODA    = Constants.CODA
TONE    = Constants.TONE
OTHER   = Constants.OTHER

REF     = Constants.REF
HYP     = Constants.HYP
EVAL    = Constants.EVAL

INF     = Constants.INF

#---------------------------------------------------------------------------#
def readLangSpecs(specPath):
  LANG_SPECS = {}
  specFile = open(specPath, 'r')
  for line in specFile:
    parts = [part.strip() for part in line.split()]
    LANG_SPECS[parts[0]] = parts[1:]
  return LANG_SPECS

#---------------------------------------------------------------------------#
def getData(hypPath, refPath):
  hyp = []
  ref = []

  hypFile = open(hypPath, 'r');
  for line in hypFile:
    hyp.append(stripTag(line))
  hypFile.close()

  refFile = open(refPath, 'r');
  for line in refFile:
    ref.append(stripTag(line))
  refFile.close()

  if len(hyp) != len(ref):
    print "Number of hyp and reference entries do not match"
    exit(1)

  return [hyp, ref];

#--------------------------------------------------------------------------#
def stripTag(line):
  parts = [part.strip() for part in line.split()]
  return ' '.join(parts[:-1])

#--------------------------------------------------------------------------#
def ComputeScliteScore(hyp, ref, hypDir):
  reportName = 'syl_errors'
  os.system(sclitePath + " -r " + ref + \
          " -h " + hyp + \
          " -i wsj -o pra -O " + hypDir + \
          " -n " + reportName)
  return os.path.join(hypDir, reportName + '.pra')

#--------------------------------------------------------------------------#
def ComputeAllSylsErrors(hyp, ref, sclitePath, LANG_SPECS):
  sylList = []

  print "Scoring"
  print "\tHyp: " + str(hyp)
  print "\tRef: " + str(ref)
  
  baseDir = os.path.dirname(os.path.abspath(__file__))
  tmpDir = os.path.join(baseDir, 'tmp')

  hPartsList = []
  rPartsList = []
  hTonesList = []
  rTonesList = []

  hypSyls = [part.strip() for part in hyp.split(SYL_DELIM)]
  refSyls = [part.strip() for part in ref.split(SYL_DELIM)]

  idx = 1
  for hSyl in hypSyls:
    for rSyl in refSyls:
      entry = (hSyl, rSyl)
      sylList.append(entry)
  
      [hParts, hTone, rParts, rTone] = SplitTones(hSyl, rSyl)
      hPartsList.append(hParts)
      hTonesList.append(hTone)
      rPartsList.append(rParts)
      rTonesList.append(rTone)
      idx = idx + 1

  [tmpOutput, tmpRef] = WriteTmpSylFiles(hPartsList, rPartsList)
  scliteReportPath = ComputeScliteScore(tmpOutput, tmpRef, tmpDir)
  [penalties, sylLvlPenalties] = ComputeSylLvlPenalties(scliteReportPath, hPartsList, hTonesList, rPartsList, rTonesList, LANG_SPECS)

  return [hypSyls, refSyls, penalties, sylLvlPenalties]


#-------------------------------------------------------------------------#
def ComputeSylLvlPenalties(scliteReportPath, hPartsList, hTonesList, rPartsList, rTonesList, LANG_SPECS):
  reportFile = open(scliteReportPath, 'r')

  tmpDir = "/".join(scliteReportPath.split("/")[:-1])
  penaltyFile = open(os.path.join(tmpDir, 'penalty_report.txt'), 'w')
  count = 0

  REF = Constants.REF
  HYP = Constants.HYP
  EVAL = Constants.EVAL

  penalties = []
  sylLvlPenalties = {}

  scliteOutput = {}
  for line in reportFile:
    line = line.strip()
    if line[:3] == REF:
      scliteOutput[REF] = line
    elif line[:3] == HYP:
      scliteOutput[HYP] = line
    elif line[:4] == EVAL:
      scliteOutput[EVAL] = line
      newSylError = SylError()

      hParts = hPartsList[count]
      hTone  = hTonesList[count]
      rParts = rPartsList[count]
      rTone  = rTonesList[count]
      newSylError.constructPen(hParts, hTone, rParts, rTone, scliteOutput, LANG_SPECS)

      count = count + 1

      penaltyFile.write(newSylError.disp())
      penalties.append(newSylError.pen)

      hSylSymbol = ' '.join(hParts + [hTone])
      hSylSymbol = tuple([hSylSymbol.strip()])
      rSylSymbol = ' '.join(rParts + [rTone])
      rSylSymbol = tuple([rSylSymbol.strip()])
      sylLvlPenalties[(hSylSymbol, rSylSymbol)] = newSylError
  
  reportFile.close()
  penaltyFile.close()

  return [penalties, sylLvlPenalties]
      

#-------------------------------------------------------------------------#
def SplitTones(hSyl, rSyl):
  hParts = [part.strip() for part in hSyl.split(SUBSYL_DELIM)]
  if hParts[-1] in LANG_SPECS[TONE]:
    hTone = hParts[-1]
    hParts = hParts[:-1]
  else:
    hTone = ''

  rParts = [part.strip() for part in rSyl.split(SUBSYL_DELIM)]
  if rParts[-1] in LANG_SPECS[TONE]:
    rTone = rParts[-1]
    rParts = rParts[:-1]
  else:
    rTone = ''
  
  return [hParts, hTone, rParts, rTone]

#-------------------------------------------------------------------------#
def WriteTmpSylFiles(hPartsList, rPartsList):
  baseDir = os.path.dirname(os.path.abspath(__file__))
  tmpDir = os.path.join(baseDir, 'tmp')

  if not os.path.exists(tmpDir):
    os.makedirs(tmpDir);

  hypSylsPath = os.path.join(tmpDir, 'tmp_hyp_syls.txt')
  refSylsPath = os.path.join(tmpDir, 'tmp_ref_syls.txt')

  hypSylsFile = open(hypSylsPath, 'w')
  refSylsFile = open(refSylsPath, 'w')

  for i in range(len(hPartsList)):
    hParts = hPartsList[i]
    rParts = rPartsList[i]
 
    idx = i+1
    hypSylsFile.write(SUBSYL_DELIM.join(hParts) + "\t\t(" + str(idx) + ")\n") 
    refSylsFile.write(SUBSYL_DELIM.join(rParts) + "\t\t(" + str(idx) + ")\n")

  hypSylsFile.close()
  refSylsFile.close()
  return [hypSylsPath, refSylsPath]

#-------------------------------------------------------------------------#
def ComputePenalties(hyp, ref):
  allErrors = []
  for i in range(len(hyp)):
    allEntryErrors = ComputeEntryPenalties(hyp[i], ref[i])
    allErrors.append(allEntryErrors) 
  return allErrors


#-------------------------------------------------------------------------#
def ComputeEntryPenalties(hyp, ref):
  [hypSyls, refSyls, penalties, sylLvlPenalties] = ComputeAllSylsErrors(hyp, ref, sclitePath, LANG_SPECS)

  penalty = {}
  path = {}
  count = 0

  hypLen = len(hypSyls)
  refLen = len(refSyls)

  for i in range(hypLen):
    for j in range(i, hypLen+1):
      for k in range(refLen):
        for l in range(k, refLen+1):
          key = (i, j, k, l)
          penalty[key] = INF
          if j == i+1 and l == k+1:
            penalty[key] = penalties[count]
            count = count + 1
          elif j == i or l == k:
            if l > k:
              penalty[key] = (l-k) * Penalty.MAX_SYL_PEN
            if j > i:
              penalty[key] = (j-i) * Penalty.MAX_SYL_PEN
              

  for len_1 in range(1, hypLen+1):
    for len_2 in range(1, refLen+1):
      for i in range(hypLen+1-len_1):
        for m in range(refLen+1-len_2):
          for j in range(i+1, i+len_1+1):
            for n in range(m+1, m+len_2+1):
              for k in range(i, j):
                for h in range(m, n):
                  # print "i, j, m, n: " + str((i, j, m, n))
                  # print "i, k, m, h: " + str((i, k, m, h))
                  # print "k, j, h, n: " + str((k, j, h, n))
                  # print ""
                  tmp = penalty[(i, k, m, h)] + penalty[(k, j, h, n)]
                  if penalty[(i, j, m, n)] > tmp:
                    penalty[(i, j, m, n)] = tmp
                    path[(i, j, m, n)] = (k, h)
  
  report = { 'hyp': [], 'ref': [], 'pen': [], 'text': [] }
  allEntryErrors = []
  DecodeAlignment(0, hypLen, 0, refLen, path, hypSyls, refSyls, sylLvlPenalties, allEntryErrors)
  for e in allEntryErrors:
    print e.disp()
  return allEntryErrors

#-------------------------------------------------------------------------#
def DecodeAlignment(i, j, m, n, path, hypSyls, refSyls, sylLvlPenalties, allEntryErrors):
  label = (i, j, m, n)
  if label not in path:
    pen = 0
    hSyl = hypSyls[i:j]
    rSyl = refSyls[m:n]

    print "\n\n"
    print str(hSyl) + " - " + str(rSyl)

    if len(hSyl) > 0 and len(rSyl) > 0:
      hSyl = tuple(hSyl)
      rSyl = tuple(rSyl)
      pen = sylLvlPenalties[(hSyl, rSyl)].pen
      sylError = sylLvlPenalties[(hSyl, rSyl)]
      allEntryErrors.append(sylError)
    else:
      sylError = SylError()
      if len(hSyl) == 0:
        fullSyl = rSyl[0]
        [sylStruct, pen, refSylStruct, alignedSylStruct] = ComputeMaxPenFromRefSyl(fullSyl)
        sylError.struct = sylStruct
        sylError.pen = pen
        sylError.ref = refSylStruct
        sylError.alignedHyp = alignedSylStruct
        sylError.hyp[OTHER] = ' '.join(sylError.alignedHyp.values()[0:-1])
        sylError.hyp[TONE] = sylError.alignedHyp[TONE]
        for l in list(sylError.struct) + [TONE]:
          sylError.errors[l] = Penalty.DEL
      elif len(rSyl) == 0:
        fullSyl = hSyl[0]
        [sylStruct, pen, refSylStruct, alignedSylStruct] = ComputeMaxPenFromHypSyl(fullSyl)
        sylError.struct = sylStruct
        sylError.pen = pen
        sylError.ref = refSylStruct
        sylError.alignedHyp = alignedSylStruct
        sylError.hyp[OTHER] = ' '.join(sylError.alignedHyp.values()[0:-1])
        sylError.hyp[TONE] = sylError.alignedHyp[TONE]
        for l in list(sylError.struct) + [TONE]:
          sylError.errors[l] = Penalty.INS
      allEntryErrors.append(sylError)
  else:
    (k, h) = path[label]
    DecodeAlignment(i, k, m, h, path, hypSyls, refSyls, sylLvlPenalties, allEntryErrors)
    DecodeAlignment(k, j, h, n, path, hypSyls, refSyls, sylLvlPenalties, allEntryErrors)

#-------------------------------------------------------------------------#
def ComputeMaxPenFromHypSyl(syl):
  parts = syl.split(' ')
  sylStruct = [ OTHER ]

  refSylStruct = { OTHER: '*', TONE: '*' }
  alignedSylStruct = { OTHER: syl, TONE: '*' }
  pen = len(parts) * Penalty.MAX_SUBSYL_PEN
  return [sylStruct, pen, refSylStruct, alignedSylStruct]
  
#-------------------------------------------------------------------------#
def ComputeMaxPenFromRefSyl(refSyl):
  newSylError = SylError()
  parts = [part.strip() for part in refSyl.split() if len(part) > 0]
  tone = parts[-1]
  fullTonelessParts = parts[0:len(parts)-1]

  newSylError.processRefSylStruct(fullTonelessParts, LANG_SPECS)

  labels = list(newSylError.struct) + [TONE]
  refSylStruct = {}
  alignedSylStruct = {}
  for i in range(len(labels)):
    l = labels[i]
    refSylStruct[l] = parts[i]
    alignedSylStruct[l] = '*'
  pen = len(labels) * Penalty.MAX_SUBSYL_PEN
  return [newSylError.struct, pen, refSylStruct, alignedSylStruct]

#-------------------------------------------------------------------------#
def reportErrors(allErrors):
  summaryPath = os.path.join(reportDir, reportName + '.summary.txt')
  fullReportPath = os.path.join(reportDir, reportName + '.full.csv')

  makeSummary(allErrors, summaryPath)
  makeFullReport(allErrors, fullReportPath)

#-------------------------------------------------------------------------#
def makeSummary(allErrors, summaryPath):
  summaryFile = open(summaryPath, 'w')
  label = [ONSET, NUCLEUS, CODA, TONE]

  stringCount = len(allErrors)
  wrongStringCount = 0
  stringWithWrongSylStructCount = 0

  wrongSylStructCount = 0
  wrongSylCount = 0
  sylCount = 0

  wrongSubsylCount = 0
  wrongSubsylCountByLabelInString = {}
  subsylCountByLabel = {ONSET: 0, NUCLEUS: 0, CODA: 0, TONE: 0}
  subsylCountByLabelInCorrectStructSyl = {ONSET: 0, NUCLEUS: 0, CODA: 0, TONE: 0}
  allWrongSubsylCountByLabel = {ONSET: {}, NUCLEUS: {}, CODA: {}, TONE: {}}
  allWrongSubsylCountByLabelInCorrectStructString = {ONSET: {}, NUCLEUS: {}, CODA: {}, TONE: {}}
  subsylCount = 0
    
  stringWithWrongTonelessSubylUnitsCount = 0
  toneWithCorrectTonelessSubsylUnitsCount = 0
  wrongToneWithCorrectTonelessSubsylUnitsCount = {}

  for i in range(stringCount):
    error = allErrors[i]
    wrongSubsylCountByLabelInString = {ONSET: {}, NUCLEUS: {}, CODA: {}, TONE: {}}
    subsylCountByLabelInString = {ONSET: 0, NUCLEUS: 0, CODA: 0, TONE: 0}

    isWrongString = False
    hasWrongSylStruct = False
    hasWrongTonelessSubsylUnits = False
    for sylError in error:
      wrongSubsylCountByLabelInSyl = {ONSET: {}, NUCLEUS: {}, CODA: {}, TONE: {}}
      sylCount = sylCount + 1
      isSylWrong = False
      isSylStructWrong = False
      for l in label:
        if l in sylError.errors:
          subsylCount = subsylCount + 1
          subsylCountByLabel[l] = subsylCountByLabel[l] + 1
          subsylCountByLabelInString[l] = subsylCountByLabelInString[l] + 1

          print "\nREF: " + str(sylError.ref)
          print "HYP: " + str(sylError.hyp)
          print "ALIGNED_HYP: " + str(sylError.alignedHyp)
          print "ERR: " + str(sylError.errors)
          if sylError.errors[l] != Penalty.CORRECT:
            subsylError = sylError.errors[l]
            isWrongString = True
            isSylWrong = True

            wrongSubsylCount = wrongSubsylCount + 1
            if subsylError == Penalty.DEL or subsylError == Penalty.INS:
               isSylStructWrong = True
               hasWrongSylStruct = True
               if l != TONE:
                 hasWrongTonelessSubsylUnits = True
            if subsylError not in wrongSubsylCountByLabelInSyl[l]:
              wrongSubsylCountByLabelInSyl[l][subsylError] = 1
            else:
              wrongSubsylCountByLabelInSyl[l][subsylError] = wrongSubsylCountByLabelInSyl[l][subsylError] + 1

            if subsylError not in allWrongSubsylCountByLabel[l]:
              allWrongSubsylCountByLabel[l][subsylError] = 1
            else:
              allWrongSubsylCountByLabel[l][subsylError] = allWrongSubsylCountByLabel[l][subsylError] + 1
      for l in label:
        for e in wrongSubsylCountByLabelInSyl[l]:
          if e not in wrongSubsylCountByLabelInString[l]:
            wrongSubsylCountByLabelInString[l][e] = wrongSubsylCountByLabelInSyl[l][e]
          else:
            wrongSubsylCountByLabelInString[l][e] = wrongSubsylCountByLabelInString[l][e] + wrongSubsylCountByLabelInSyl[l][e]


      if isSylWrong:
        wrongSylCount = wrongSylCount + 1
      if isSylStructWrong:
        wrongSylStructCount = wrongSylStructCount + 1
    if hasWrongSylStruct:
      stringWithWrongSylStructCount = stringWithWrongSylStructCount + 1
    else:
      for l in label:
        subsylCountByLabelInCorrectStructSyl[l] = subsylCountByLabelInCorrectStructSyl[l] + subsylCountByLabelInString[l]
        for e in wrongSubsylCountByLabelInString[l]:
          if e not in allWrongSubsylCountByLabelInCorrectStructString[l]:
            allWrongSubsylCountByLabelInCorrectStructString[l][e] = wrongSubsylCountByLabelInString[l][e]
          else:
            allWrongSubsylCountByLabelInCorrectStructString[l][e] = allWrongSubsylCountByLabelInCorrectStructString[l][e] + wrongSubsylCountByLabelInString[l][e]

    if hasWrongTonelessSubsylUnits:
      stringWithWrongTonelessSubylUnitsCount = stringWithWrongTonelessSubylUnitsCount + 1
    else:
      if TONE in wrongSubsylCountByLabelInString:
        for e in wrongSubsylCountByLabelInString[TONE]:
          if e not in wrongToneWithCorrectTonelessSubsylUnitsCount:
            wrongToneWithCorrectTonelessSubsylUnitsCount[e] = 0
          wrongToneWithCorrectTonelessSubsylUnitsCount[e] = wrongToneWithCorrectTonelessSubsylUnitsCount[e] + wrongSubsylCountByLabelInString[TONE][e]
          toneWithCorrectTonelessSubsylUnitsCount = toneWithCorrectTonelessSubsylUnitsCount + len(error)
      

    if isWrongString:
      wrongStringCount = wrongStringCount + 1 
  
  summaryFile.write('String error rate: ' + getErrorFormat(wrongStringCount, stringCount) + '\n')
  summaryFile.write('Syllable error rate: ' + getErrorFormat(wrongSylCount, sylCount) + '\n')
  summaryFile.write('Subsyllabic unit error rate: ' + getErrorFormat(wrongSubsylCount, subsylCount) + '\n')
  for l in label:
    overallError = sum(allWrongSubsylCountByLabel[l].values()) 
    summaryFile.write('\t' + l + ': ' + getErrorFormat(overallError, subsylCountByLabel[l]) + '\n')
    for e in allWrongSubsylCountByLabel[l]:
      summaryFile.write('\t\t' + e + ': ' + getErrorFormat(allWrongSubsylCountByLabel[l][e], overallError) + '\n')
  
  summaryFile.write('\nString with wrong syllabic structure: ' + getErrorFormat(stringWithWrongSylStructCount , stringCount) + '\n')
  summaryFile.write('Out of ' + getErrorFormat(stringCount - stringWithWrongSylStructCount, stringCount) + ' strings with correct syllabic structure: \n')
  for l in label:
    overallError = sum(allWrongSubsylCountByLabelInCorrectStructString[l].values()) 
    if subsylCountByLabelInCorrectStructSyl[l] > 0:
      summaryFile.write('\t' + l + ': ' + getErrorFormat(overallError, subsylCountByLabelInCorrectStructSyl[l]) + '\n')
    for e in allWrongSubsylCountByLabelInCorrectStructString[l]:
      summaryFile.write('\t\t' + e + ': ' + getErrorFormat(allWrongSubsylCountByLabelInCorrectStructString[l][e], overallError) + '\n')
  
  summaryFile.write('\nString with wrong toneless subsyllabic units ' + getErrorFormat(stringWithWrongTonelessSubylUnitsCount , stringCount) + '\n')
  summaryFile.write('Out of ' + getErrorFormat(stringCount - stringWithWrongTonelessSubylUnitsCount, stringCount) + ' strings with correct toneless subsyllabic units: \n')

  for e in wrongToneWithCorrectTonelessSubsylUnitsCount:
    summaryFile.write('\t' + e + ': ' + getErrorFormat(wrongToneWithCorrectTonelessSubsylUnitsCount[e], toneWithCorrectTonelessSubsylUnitsCount) + '\n')
    
  summaryFile.close()

#-------------------------------------------------------------------------#
def getErrorFormat(errorCount, count):
  return '{0:.2f}'.format(errorCount * 100.0/count) + '% (' + str(errorCount) + '/' + str(count) + ')'
  

#-------------------------------------------------------------------------#
def makeFullReport(allErrors, fullReportPath):
  DELIM = ', '
  fullReportFile = open(fullReportPath, 'w')
  label = [ONSET, NUCLEUS, CODA, TONE]

  for i in range(len(allErrors)):
    error = allErrors[i]

    refEntry = []
    hypEntry = []
    errorEntry = []
    for sylError in error:
      refTmp = []
      hypTmp = []
      errorTmp = []
      print sylError.ref
      print sylError.alignedHyp
      for l in label:
        if l in sylError.errors:
          refTmp.append(sylError.ref[l])
          hypTmp.append(sylError.alignedHyp[l])
          if sylError.errors[l] != Penalty.CORRECT:
            errorTmp.append(sylError.errors[l] + ' (' + l[0] + ')')
          else:
            errorTmp.append(' ')
      refEntry.append(DELIM.join(refTmp))
      hypEntry.append(DELIM.join(hypTmp))
      errorEntry.append(DELIM.join(errorTmp))
    txt = str(i+1) + ', '
    txt = txt + (DELIM + DELIM).join(refEntry) + '\n'
    fullReportFile.write(txt)
    txt = ' ' + DELIM + (DELIM + DELIM).join(hypEntry) + '\n'
    fullReportFile.write(txt)
    txt = ' ' + DELIM + (DELIM + DELIM).join(errorEntry) + '\n'
    fullReportFile.write(txt)
     
  fullReportFile.close()


print hypPath
print refPath

[hyp, ref] = getData(hypPath, refPath)
LANG_SPECS = readLangSpecs(refLangSpecsPath)
allErrors = ComputePenalties(hyp, ref)

reportErrors(allErrors)
