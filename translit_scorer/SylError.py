import sys

from Constants import Constants
from Penalty import Penalty

class SylError:
  def __init__(self):
    self.ref = {}
    self.hyp = {}
    self.alignedHyp = {}
    self.struct = ()

    self.errors   = {}
    self.errors[Constants.OTHER] = []

    self.pen = 0

  def disp(self):
    labels = [Constants.ONSET, \
            Constants.NUCLEUS, \
            Constants.CODA, \
            Constants.TONE]

    s = "REF:\t\t{ "
    for l in labels:
      if l in self.ref:
        s = s + l + ": " + self.ref[l] + ", "
    s = s + "}\n"

    s = s +  "HYP:\t\t{ " + Constants.OTHER + ": " + ' '.join(self.hyp[Constants.OTHER]) + \
            ", "  + Constants.TONE + ": " + self.hyp[Constants.TONE] + " }\n"

    s = s +  "ALIGNED HYP:\t{ "
    for l in labels:
      if l in self.alignedHyp:
        s = s + l + ": " + self.alignedHyp[l] + ", "
    s = s + "}\n"
    s = s +  "STRUCT:\t\t" + str(self.struct) + "\n"

    s = s +  "ERRORS:\t\t{ "
    for l in labels:
      if l in self.errors:
        s = s + l + ": " + self.errors[l] + ", "
    if len(self.errors[Constants.OTHER]) > 0:
      s = s + Constants.OTHER + ": " + str(self.errors[Constants.OTHER])
    s = s + "}\n"

    s = s +  "PENALTY:\t" + str(self.pen) + "\n\n"
    return s

  def evalScliteOutput(self, hParts, scliteOutput):
    ref = scliteOutput[Constants.REF][6:] + Constants.DELIM
    hyp = scliteOutput[Constants.HYP][6:] + Constants.DELIM
    err = scliteOutput[Constants.EVAL][6:] + Constants.DELIM

    rTok = ''
    hTok = ''
    errTok = ''
    rTokCount = 0
    hTokCount = 0

    count = 0
    for i in range(len(ref)):
      rTok = rTok.strip()
      hTok = hTok.strip()
      errTok = errTok.strip()

      if ref[i] == Constants.DELIM:
        if len(rTok) > 0:
          if Constants.DELETED not in rTok:
            if errTok == '':
              errTok = Constants.CORRECT

            label = self.struct[rTokCount]
            self.errors[label] = errTok
            self.alignedHyp[label] = hTok

            rTokCount = rTokCount + 1
          else:
            self.errors[Constants.OTHER].append(errTok)

          if Constants.DELETED not in hTok:
            hTokCount = hTokCount + 1

          rTok = ''
          hTok = ''
          errTok = ''
      else:
        rTok = rTok + ref[i]
        if i < len(hyp):
          hTok = hTok + hyp[i]
        if i < len(err):
          errTok = errTok + err[i]
    # print self.ref
    # print self.alignedHyp
    # print self.errors


  def constructPen(self, hParts, hTone, rParts, rTone, scliteOutput, langSpecs):
    self.processRefSylStruct(rParts, langSpecs)
    self.evalScliteOutput(hParts, scliteOutput)

    self.hyp[Constants.TONE] = hTone
    self.hyp[Constants.OTHER] = hParts
    self.ref[Constants.TONE] = rTone
    self.alignedHyp[Constants.TONE] = hTone

    self.errors[Constants.TONE] = Constants.CORRECT
    if hTone != rTone:
      self.errors[Constants.TONE] = Constants.SUB
    elif hTone == '':
      self.errors[Constants.TONE] = Constants.DEL

    self.computePen()
    self.correctAlignedHyp(hParts)

  def correctAlignedHyp(self, hParts):
    # print hParts
    # print self.alignedHyp
    count = 0
    for l in self.alignedHyp:
      if l != Constants.TONE and Constants.DELETED not in self.alignedHyp[l]:
        self.alignedHyp[l] = hParts[count]
        count = count + 1
      elif Constants.DELETED in self.alignedHyp[l]:
        self.alignedHyp[l] = Constants.DELETED

  def computePen(self):
    self.pen = 0
    # print "\tERRORS"
    # print self.errors
    # print "\tREF"
    # print self.ref
    for label in [Constants.ONSET, Constants.NUCLEUS, Constants.CODA, Constants.TONE]:
      if label in self.errors:
        err = self.errors[label]
        self.pen = self.pen + Penalty.vals[label][err]
    for err in self.errors[Constants.OTHER]:
      if err:
        self.pen = self.pen + Penalty.vals[Constants.OTHER][err]


  def processRefSylStruct(self, rParts, langSpecs):
    if len(rParts) == 3:
      self.ref[Constants.ONSET] = rParts[0]
      self.ref[Constants.NUCLEUS] = rParts[1]
      self.ref[Constants.CODA] = rParts[2]
      self.struct = (Constants.ONSET, Constants.NUCLEUS, Constants.CODA, ) 
    elif len(rParts) == 2:
      if rParts[0] in langSpecs[Constants.NUCLEUS]:
        self.ref[Constants.NUCLEUS] = rParts[0]
        self.ref[Constants.CODA] = rParts[1]
        self.struct = (Constants.NUCLEUS, Constants.CODA, )
      if rParts[0] in langSpecs[Constants.ONSET]:
        self.ref[Constants.ONSET] = rParts[0]
        self.ref[Constants.NUCLEUS] = rParts[1]
        self.struct = (Constants.ONSET, Constants.NUCLEUS, )
    elif len(rParts) == 1:
      self.ref[Constants.NUCLEUS] = rParts[0]
      self.struct = (Constants.NUCLEUS, )
    else:
      print("Reference syllable with an invalid length!")
      print "Syllable: " + str(rParts)
      sys.exit(1)

#  newSylErr = SylError()
#  sample = {}
#  dummy = {'NUCLEUS': ['@I'], 'ONSET': ['f']}

#  sample['REF']  = 'REF:  b_< U K'
#  sample['HYP']  = 'HYP:  b_< * O'
#  sample['Eval'] = 'Eval:     D S'
#  rParts = ['b_<','u', 'k']
#  rTone = '_3'
#  hParts = ['b_<', 'o']
#  hTone  = '_2'
#  # newSylErr.processRefSylStruct(rParts, dummy)
#  # newSylErr.evalScliteOutput(hParts, sample)
#  newSylErr.constructPen(hParts, hTone, rParts, rTone, sample, dummy)
#  
#  sample['REF']  = 'REF:  b_< U K'
#  sample['HYP']  = 'HYP:  d   U O'
#  sample['Eval'] = 'Eval: S     S'
#  hParts = ['d', 'u', 'o']
#  hTone  = ''
#  # newSylErr.processRefSylStruct(rParts, dummy)
#  # newSylErr.evalScliteOutput(hParts, sample)
#  newSylErr.constructPen(hParts, hTone, rParts, rTone, sample, dummy)
#  
#  sample['REF']  = 'REF:  b_< U K'
#  sample['HYP']  = 'HYP:  d   U O'
#  sample['Eval'] = 'Eval: S      '
#  # newSylErr.processRefSylStruct(rParts, dummy)
#  # newSylErr.evalScliteOutput(hParts, sample)
#  newSylErr.constructPen(hParts, hTone, rParts, rTone, sample, dummy)
#  
#  sample['REF']  = 'REF:  s * * @: n'
#  sample['HYP']  = 'HYP:  * R U @: N'
#  sample['Eval'] = 'Eval: D I I C  S'
#  rParts = ['s', '@:', 'n']
#  hParts = ['r', 'u', '@:', 'n']
#  # newSylErr.processRefSylStruct(rParts, dummy)
#  # newSylErr.evalScliteOutput(hParts, sample)
#  newSylErr.constructPen(hParts, hTone, rParts, rTone, sample, dummy)

#  sample['REF']  = 'REF:  *** F @I'
#  sample['HYP']  = 'HYP:  B_< U K'
#  sample['Eval'] = 'Eval: I   S S'
#  rParts = ['f','@I']
#  rTone = '_1'
#  hParts = ['b_<', 'u', 'k']
#  hTone  = '_2'
#  # newSylErr.processRefSylStruct(rParts, dummy)
#  # newSylErr.evalScliteOutput(hParts, sample)
#  newSylErr.constructPen(hParts, hTone, rParts, rTone, sample, dummy)
#  print newSylErr.disp()
