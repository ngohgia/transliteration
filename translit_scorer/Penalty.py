from Constants import Constants

class Penalty:
  CORRECT = Constants.CORRECT
  SUB     = Constants.SUB
  DEL     = Constants.DEL
  INS     = Constants.INS

  ONSET   = Constants.ONSET
  NUCLEUS = Constants.NUCLEUS
  CODA    = Constants.CODA
  TONE    = Constants.TONE
  OTHER   = Constants.OTHER

  vals = {
    ONSET: { CORRECT: 0, INS: 3, DEL: 3, SUB: 4 },
    NUCLEUS: { CORRECT: 0, INS: 3, DEL: 3, SUB: 4 },
    CODA: { CORRECT: 0, INS: 3, DEL: 3, SUB: 4 },
    TONE: { CORRECT: 0, DEL: 3, SUB: 4 },
    OTHER: { CORRECT: 0, INS: 3, DEL: 3, SUB: 4 },
  }

  MAX_SUBSYL_PEN = 4
  MAX_SYL_PEN = 4 * MAX_SUBSYL_PEN
