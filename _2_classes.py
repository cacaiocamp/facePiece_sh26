class MiniatureRecording:
    def __init__(self):
        self.number = 0
        self.duration = 0
        self.wait = 0
        self.type = 0
        self.fileName = "null"
        self.filePath = "null"
        self.fileReady = False

class AudienceRecordingPlayer:
    def __init__(self):
        self.number = 0
        self.possibleColumns = []
        self.columnLayerToPlay = [0, 0, 0]
        self.recordingsSelected = [0, 0, 0]
        self.thisPlayDuration = 2
        self.nextPlayDuration = 2
        self.curColumnIndex = 0
        self.curColumnsCleared = [False, False, False]
        self.playingThread = 'null'
        self.operationThread = 'null'
        self.minRecordings = 1

        self.blankChosen = False
        self.nextRecordingPastPerformance = False

    def getNextColumnIndex(self):
        nextColumnIndex = self.curColumnIndex + 1

        if(nextColumnIndex > 2):
            nextColumnIndex = 0
        
        return nextColumnIndex
    
    def getLastColumnIndex(self):
        lastColumnIndex = self.curColumnIndex - 1

        if(lastColumnIndex < 0):
            lastColumnIndex = 2
        
        return lastColumnIndex
    
    def getNextColumn(self):
        return self.possibleColumns[self.getNextColumnIndex()]
    
    def getNoClipColumnIndex(self):
        return self.possibleColumns[0] - 1

class Column:
    def __init__(self):
        self.number = 0
        self.cleared = True
        
class Clip:
    def __init__(self):
        self.layer = 0
        self.miniatureRecording = "null"
        self.cleared = False