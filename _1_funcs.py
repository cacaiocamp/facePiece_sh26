import threading
import time
import random
import requests
import pickle
import os
import sys
import _3_gvars as gvars

def oscFunc_startStopRecording(startOrStop = 0):
    gvars.resolume_OSCCLIENT.send_message('/composition/recorder/record', [startOrStop])        

    if gvars.print_AllOSCMessages == True:
        print(f"- M --- RECORD BUTTON set to {startOrStop}")

def oscFunc_selectCameraLayer():
    gvars.resolume_OSCCLIENT.send_message('/composition/columns/1/connect', [1])        
    #gvars.curColumn = 1

    if gvars.print_AllOSCMessages == True:
        print("Connected [COLUMN 1] -- Recording [LAYER 13]")

def oscFunc_connectClip(layer, column):
    gvars.resolume_OSCCLIENT.send_message(f'/composition/layers/{layer}/clips/{column}/connect', [1])        
    #gvars.curColumn = 1

    if gvars.print_AllOSCMessages == True:
        print(f"- M -- Connected clip on [LAYER {layer}] [COLUMN {column}]")

def restFunc_clearClipSource(layer_index, clip_index):
    url = f"{gvars.resolume_BASERESTURL}/composition/layers/{layer_index}/clips/{clip_index}/clear"

    headers = {
        "Content-Type": "application/json"
    }

    try:
        #print("--D: CLEAR - BEFORE POST")
        response = requests.post(url,headers=headers)
        #print("--D: CLEAR - AFTER POST")
        response.raise_for_status()  # Raise an error for bad status codes
        #print("--D: CLEAR - AFTER RAISE")
        #print(f"Success: Cleared layer {layer_index}, clip {clip_index}")

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if response.text:
            print("Response:", response.text)
        return False

def restFunc_setClipSource(layer_index, clip_index, file_path):
    url = f"{gvars.resolume_BASERESTURL}/composition/layers/{layer_index}/clips/{clip_index}/open"

    headers = {
        "Content-Type": "application/json"
    }

    try:
        #print("--D: OPEN - BEFORE POST")
        response = requests.post(url, data=file_path,headers=headers)
        #print("--D: OPEN - AFTER POST")
        response.raise_for_status()  # Raise an error for bad status codes
        #print("--D: AFTER RAISE")
        #print(f"Success: Loaded {file_path} into layer {layer_index}, clip {clip_index}")

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if response.text:
            print("Response:", response.text)
        return False

def startNewRecording(miniatureRecording):
    if gvars.resolume_recordingAvailable == True:
        gvars.resolume_recordingAvailable = False

        interactiveScoreType = random.randint(0, (len(gvars.interactionScores_possibleColumns) - 1))

        miniatureRecording.number = gvars.recording_count
        miniatureRecording.type = interactiveScoreType
        miniatureRecording.duration = gvars.interactionScores_possibleRecDurations[interactiveScoreType]
        miniatureRecording.wait = gvars.interactionScores_possibleWaitDurations[interactiveScoreType]

        gvars.thread_recording = threading.Thread(target=recordingThread, args=(miniatureRecording,))
        gvars.thread_recording.start()
    else:
        print("- W --- RECORDING ALREADY RUNNING, NEW FORBIDDEN")

def startPlayingThreads():
    gvars.l_audiencePlayers[0].playingThread = threading.Thread(target=playingThread, args=(0,))
    gvars.l_audiencePlayers[0].playingThread.start()

    gvars.l_audiencePlayers[1].playingThread = threading.Thread(target=playingThread, args=(1,))
    gvars.l_audiencePlayers[1].playingThread.start()
    
    gvars.l_audiencePlayers[2].playingThread = threading.Thread(target=playingThread, args=(2,))
    gvars.l_audiencePlayers[2].playingThread.start()

def startFacePieceThread():    
    gvars.facePieceThread = threading.Thread(target=facePieceThread)
    gvars.facePieceThread.start()

def setNextFacePieceColumnIndex():
    gvars.curFacePieceIndex = gvars.curFacePieceIndex + 1

    if gvars.curFacePieceIndex > 9:
        gvars.curFacePieceIndex = 0

def clearAudienceColumn(audiencePlayerIndex, columnIndex):
    columnNum = gvars.l_audiencePlayers[audiencePlayerIndex].possibleColumns[columnIndex]

    for i in range(gvars.audienceLayersTotal):
        restFunc_clearClipSource(i+1, columnNum)
    
    gvars.l_audiencePlayers[audiencePlayerIndex].curColumnsCleared[columnIndex] = True

def checkTooManyBlanks():
    howManyBlanks = 0

    for i in range(3):
        if gvars.l_audiencePlayers[i].blankChosen == True:
            howManyBlanks = howManyBlanks + 1

    triggerMin = 0

    if len(gvars.l_availableRecordings) >= 7:
        triggerMin = 2
    elif len(gvars.l_availableRecordings) >= 3:
        triggerMin = 1

    if howManyBlanks >= triggerMin:
        return True 
    else:
        return False

def decideNextClipsOperation(audiencePlayerIndex):
    #setNextColumnToTrigger()
    #setNextTypePlaying()

    # pega indices e numeros para uso ao longo da funcao
    curColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].curColumnIndex

    lastColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].getLastColumnIndex()

    lastColumnNumber = gvars.l_audiencePlayers[audiencePlayerIndex].possibleColumns[lastColumnIndex]

    lastLayerNumber = gvars.l_audiencePlayers[audiencePlayerIndex].columnLayerToPlay[lastColumnIndex]
    
    # limpa o clip da ultima coluna tocada e libera a flag da coluna
    if lastLayerNumber != 0:
        restFunc_clearClipSource(lastLayerNumber, lastColumnNumber)

        gvars.l_audiencePlayers[audiencePlayerIndex].curColumnsCleared[lastColumnIndex] = True

    if gvars.l_audiencePlayers[audiencePlayerIndex].columnLayerToPlay[lastColumnIndex] != 0:
        gvars.l_curAvailableLayers.append(lastLayerNumber)
            
    if len(gvars.l_availableRecordings) > 0:
        # --- preparando a proxima coluna
        nextColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].getNextColumnIndex()

        # inicializa variaveis para a proxima coluna
        nextLayerToTrigger = 0
        nextRecordingToUse = 0
        
        # encontra novo indice de layer
        indexAuxLayer = random.randint(0, (len(gvars.l_curAvailableLayers) - 1))

        # seta como a proximo a ser usado e remove do array de layers disponiveis
        nextLayerToTrigger = gvars.l_curAvailableLayers[indexAuxLayer]
        gvars.l_curAvailableLayers.remove(nextLayerToTrigger)
        
        # adiciona como proximo layer a ser usada no vetor do audiencePlayer
        gvars.l_audiencePlayers[audiencePlayerIndex].columnLayerToPlay[nextColumnIndex] = nextLayerToTrigger

        # encontra o numero da proxima coluna a ser trigada
        nextColumnToTrigger = gvars.l_audiencePlayers[audiencePlayerIndex].possibleColumns[nextColumnIndex]

        blankChance = random.randint(0, 100)

        tooManyBlanks = checkTooManyBlanks()

        if (blankChance > 15) or (tooManyBlanks == True):

            lastPerformanceChance = 0

            if gvars.allowLastPerformancesRecordings == True and len(gvars.l_lastPerformancesRecordings) > 0:
                lastPerformanceChance = random.randint(0, 100)
            
            if lastPerformanceChance > 59:
                indexAux = random.randint(0, (len(gvars.l_lastPerformancesRecordings) - 1))

                nextRecordingToUse = indexAux

                gvars.l_audiencePlayers[audiencePlayerIndex].recordingsSelected[nextColumnIndex] = nextRecordingToUse

                gvars.l_audiencePlayers[audiencePlayerIndex].nextRecordingPastPerformance = True

                gvars.l_audiencePlayers[audiencePlayerIndex].nextPlayDuration = gvars.l_lastPerformancesRecordings[nextRecordingToUse].duration
            else:
                # encontra novo indice de gravacao
                indexAux = random.randint(0, (len(gvars.l_availableRecordings) - 1))

                # seta como a proxima a ser usada e remove do array de gravacoes disponiveis
                nextRecordingToUse = gvars.l_availableRecordings[indexAux]
                # gvars.l_availableRecordings.remove(nextRecordingToUse)

                # adiciona como proxima gravacao a ser usada no vetor do audiencePlayer
                gvars.l_audiencePlayers[audiencePlayerIndex].recordingsSelected[nextColumnIndex] = nextRecordingToUse

                gvars.l_audiencePlayers[audiencePlayerIndex].nextRecordingPastPerformance = False

                gvars.l_audiencePlayers[audiencePlayerIndex].nextPlayDuration = gvars.l_miniatureRecordings[nextRecordingToUse].duration

            # adiciona gravacao no layer e coluna encontrados
            setupNextOperationColumn(nextLayerToTrigger, nextColumnToTrigger, nextRecordingToUse, audiencePlayerIndex)     

            gvars.l_audiencePlayers[audiencePlayerIndex].blankChosen = False           
        else:
            gvars.l_audiencePlayers[audiencePlayerIndex].blankChosen = True

def setupNextOperationColumn(layerNumber, columnNumber, recordingIndex, audiencePlayerIndex):
    #print(recordings)
    #print(layers)
    recording = None

    nextColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].getNextColumnIndex()

    if gvars.l_audiencePlayers[audiencePlayerIndex].curColumnsCleared[nextColumnIndex] == True:
        if gvars.l_audiencePlayers[audiencePlayerIndex].nextRecordingPastPerformance == True:
            recording = gvars.l_lastPerformancesRecordings[recordingIndex]
        else:
            recording = gvars.l_miniatureRecordings[recordingIndex]

        # print("SET CLIP")
        # print(recordingIndex)
        # print(recording.filePath)
        if (recording.fileReady == True) or (gvars.l_audiencePlayers[audiencePlayerIndex].nextRecordingPastPerformance == True):
            restFunc_setClipSource(layerNumber, columnNumber,recording.filePath)
            gvars.l_audiencePlayers[audiencePlayerIndex].nextRecordingPastPerformance = False
            #print(f"Layer {layer} - {recording.fileName}--POST OK")
            gvars.l_audiencePlayers[audiencePlayerIndex].curColumnsCleared[nextColumnIndex] = False
    else:
        print(f"- E! --- Column {columnNumber} not cleared yet. Cannot set clip source") 

# Threads
def recordingThread(miniatureRecording):
    try:
        while True:
            oscFunc_connectClip(gvars.interactionScore_layer, gvars.interactionScores_possibleColumns[miniatureRecording.type])

            time.sleep(miniatureRecording.wait)

            oscFunc_startStopRecording(1)

            time.sleep(miniatureRecording.duration)
            break
    finally:
        print(f"- M --- REC {gvars.recording_count} recorded")

        oscFunc_startStopRecording(0)
        # time.sleep(0.0416)

        gvars.recording_count = gvars.recording_count + 1

        gvars.resendingRecordingOff = True
        gvars.thread_waitForUse = threading.Thread(target=recording_waitForUseThread, args=(miniatureRecording,))
        gvars.thread_waitForUse.start()

def recording_waitForUseThread(miniatureRecording):
    try:
        while True:
            time.sleep(0.0416)
            oscFunc_startStopRecording(0)

            time.sleep(0.0416)
            oscFunc_startStopRecording(0)

            time.sleep(miniatureRecording.duration/2)
            break

    finally:
        gvars.resolume_recordingAvailable = True
        lastRecordingCount = (gvars.recording_count - 1) + len(gvars.l_lastPerformancesRecordings)

        # gvars.recording_availableCount = gvars.recording_availableCount + 1

        lastFileName = f"facePiece_shanghai_portrait - Layer 13({lastRecordingCount + 2})"
        lastFilePath = f"file:///C:/Users/gudig/Documents/facePiece/instalacao_shanghai/intalationVids/audienceRec/facePiece_shanghai_main%20-%20Recording({lastRecordingCount + 2}).mov"

        if gvars.print_AllThreadMessages:
            print(f"--D: recType {miniatureRecording.type}")

        miniatureRecording.fileReady = True
        miniatureRecording.fileName = lastFileName
        miniatureRecording.filePath = lastFilePath
        gvars.l_miniatureRecordings.append(miniatureRecording)
        gvars.l_availableRecordings.append(miniatureRecording.number)

        gvars.allRecordingsSaved = False

def playingThread(audiencePlayerIndex):
    try:

        while True:
            if gvars.clipsPlaying == True:
                if (len(gvars.l_availableRecordings) >= gvars.l_audiencePlayers[audiencePlayerIndex].minRecordings):
                    gvars.l_audiencePlayers[audiencePlayerIndex].curColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].getNextColumnIndex()

                    gvars.l_audiencePlayers[audiencePlayerIndex].thisPlayDuration = gvars.l_audiencePlayers[audiencePlayerIndex].nextPlayDuration

                    gvars.l_audiencePlayers[audiencePlayerIndex].operationThread = threading.Thread(target=operationThread, args=(audiencePlayerIndex,))
                    gvars.l_audiencePlayers[audiencePlayerIndex].operationThread.start()

                    #print(f"-D----- time to wait {gvars.l_audiencePlayers[audiencePlayerIndex].thisPlayDuration} seconds")

                time.sleep(gvars.l_audiencePlayers[audiencePlayerIndex].thisPlayDuration)
            else:
                noClipColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].getNoClipColumnIndex()

                for columnIndex in range(3):
                    clearAudienceColumn(audiencePlayerIndex, columnIndex) # Clear the columns

                    oscFunc_connectClip(gvars.l_audiencePlayers[audiencePlayerIndex].columnLayerToPlay[columnIndex], noClipColumnIndex)

                gvars.l_curAvailableLayers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                
                break
    finally:
        print(f"- M ---------- playingThread {audiencePlayerIndex} closed")

def operationThread(audiencePlayerIndex):
    try:
        while True:
            curColumnIndex = gvars.l_audiencePlayers[audiencePlayerIndex].curColumnIndex

            clipLayer = gvars.l_audiencePlayers[audiencePlayerIndex].columnLayerToPlay[curColumnIndex]

            clipColumn = gvars.l_audiencePlayers[audiencePlayerIndex].possibleColumns[curColumnIndex]

            if (clipLayer != 0) and (clipColumn != 0):
                oscFunc_connectClip(clipLayer, clipColumn)

            decideNextClipsOperation(audiencePlayerIndex)

            break
    finally:
        if gvars.print_AllThreadMessages:
            print("---------- operationThread closed")

def facePieceThread():
    try:
        while True:
            if gvars.facePieceRunning:
                setNextFacePieceColumnIndex()

                if gvars.facePieceRunning:
                    oscFunc_connectClip(gvars.facePieceLayer, gvars.l_possibleFacePieceColumns[gvars.curFacePieceIndex])

                    print(f"- M --- facePiece playing on column {gvars.l_possibleFacePieceColumns[gvars.curFacePieceIndex]}")

                time.sleep(gvars.facePieceDur)

                oscFunc_connectClip(gvars.facePieceLayer, gvars.facePieceNoClipColumn)

                time.sleep(3)

                if gvars.facePieceRunning:
                    oscFunc_connectClip(gvars.creditsLayer, gvars.creditsColumn)

                time.sleep(gvars.creditsDur)

                oscFunc_connectClip(gvars.creditsLayer, gvars.facePieceNoClipColumn)

                time.sleep(5)
            else:
                break
    finally:
        print("---------- facePieceThread closed")

# save load miniature recordings
def saveRecordings():
    """Save the global array to a file using pickle."""

    listToSave = gvars.l_miniatureRecordings + gvars.l_lastPerformancesRecordings
    with open(gvars.RECORDINGS_SAVE_FILE, "wb") as f:
        pickle.dump(listToSave, f)

    print(f"Saved {len(listToSave)} recordings to {gvars.RECORDINGS_SAVE_FILE}")

    gvars.allRecordingsSaved = True

def loadRecordingsSeparately():
    """Load the global array from the file (if it exists)."""
    if os.path.exists(gvars.RECORDINGS_SAVE_FILE):
        with open(gvars.RECORDINGS_SAVE_FILE, "rb") as f:
            gvars.l_lastPerformancesRecordings = pickle.load(f)

        print(f"Loaded {len(gvars.l_lastPerformancesRecordings)} recordings from {gvars.RECORDINGS_SAVE_FILE} into l_lastPerformancesRecordings")

        gvars.recordingsLoaded = True
    else:
        print("No save file found. Starting with empty list.")