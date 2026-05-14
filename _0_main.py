from oscpy.client import OSCClient
import cv2
import numpy as np
import _1_funcs as funcs
import _2_classes as classes
import _3_gvars as gvars

# Initialize audience players
for playerIndex in range(3):
    audiencePlayer = classes.AudienceRecordingPlayer()
    audiencePlayer.number = playerIndex
    audiencePlayer.possibleColumns = gvars.audiencePlayers_possibleColumns[playerIndex]
    audiencePlayer.minRecordings = gvars.l_minRecordingsForPlayers[playerIndex]
    
    audiencePlayer.waitTimeTillNextPlay = 2
    audiencePlayer.curColumnIndex = 0

    gvars.l_audiencePlayers.append(audiencePlayer)

    for columnIndex in range(3):
        funcs.clearAudienceColumn(playerIndex, columnIndex) # Clear the columns at the start

try:

    funcs.oscFunc_selectCameraLayer()
    
    while True:    
        # Create a simple blank window
        img = np.zeros((480, 640, 3), dtype=np.uint8)  # Black image
        
        # draw information
        facePieceShanghaiText = "facePiece Shanghai - YOUNG Theatre"
        clipsPlayingText = "clips PLAYING" if gvars.clipsPlaying else "clips paused"
        facePieceText = "facePiece RUNNING" if gvars.facePieceRunning else "facePiece paused"
        recordingText = "recording off" if gvars.resolume_recordingAvailable else "RECORDING ON"
        numberOfRecordingsText = f"audience recordings: {gvars.recording_count}"
        availableRecordingsText = f"available recordings: {len(gvars.l_availableRecordings)}"
        lastPerformancesRecordingsText = f"last performance recordings: {len(gvars.l_lastPerformancesRecordings)}"
        resolumeConnectedToText = f"resolume connected to: {gvars.resolume_OSCIP}"
        lastPerformancesAllowedText = "past recordings ALLOWED" if gvars.allowLastPerformancesRecordings else "past recordings off"

        allRecordingsSavedText = "all recordings saved!" if gvars.allRecordingsSaved else "recordings NOT SAVED"
        recordingsLoadedText = "recordings loaded!" if gvars.recordingsLoaded else "recordings NOT LOADED"
        
        cv2.putText(img, facePieceShanghaiText, (60, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, clipsPlayingText, (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, facePieceText, (60, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, resolumeConnectedToText, (60, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv2.putText(img, allRecordingsSavedText, (60, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, recordingsLoadedText, (60, 330), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, lastPerformancesAllowedText, (60, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(img, recordingText, (440, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, numberOfRecordingsText, (408, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, availableRecordingsText, (410, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(img, lastPerformancesRecordingsText, (342, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # wait for key
        key = cv2.waitKey(33) & 0xFF

        if key == ord('q'): 
            if gvars.allRecordingsSaved == False and gvars.saveWarningGiven == False:
                print("- W! --- Recordings not saved!")
                gvars.saveWarningGiven = True
            else:
                break
        # elif key == ord('e'): # select recording cam layer
        #     funcs.oscFunc_selectCameraLayer()
        elif key == ord(' '): 
            gvars.clipsPlaying = not gvars.clipsPlaying
            if gvars.clipsPlaying == True:
                funcs.startPlayingThreads()
        elif key == ord('r'): 
            if gvars.facePieceRunning:
                print("--W! - facePiece already running")
            else:
                miniatureRecording = classes.MiniatureRecording()
                funcs.startNewRecording(miniatureRecording)
            #funcs.oscFunc_startStopRecording(1)
        elif key == ord('0'):
            funcs.saveRecordings()
        elif key == ord('l'):
            funcs.loadRecordingsSeparately()
        elif key == ord('a'):
            gvars.allowLastPerformancesRecordings = not gvars.allowLastPerformancesRecordings
        # elif key == ord('p'):
        #     funcs.loadRecordingSameList()
        elif key == ord('1'): 
            gvars.facePieceRunning = not gvars.facePieceRunning

            if gvars.facePieceRunning:
                funcs.startFacePieceThread()
            else:
                funcs.oscFunc_connectClip(gvars.facePieceLayer, gvars.facePieceNoClipColumn)
        # elif key == ord('p'): 
        #     funcs.printAllRecordings()
        # elif key == ord('1'): 
        #     gvars.shortClipsOperationPossible = not gvars.shortClipsOperationPossible

        cv2.imshow('mainWindow - facePieceShanghai', img)
except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close all OpenCV windows
    cv2.destroyAllWindows()
    #timingThread.join()

    # for playerIndex in range(3):
    #     gvars.l_audiencePlayers[playerIndex].playingThread.join()
    #     gvars.l_audiencePlayers[playerIndex].operationThread.join()

    print("---------- Code closed")