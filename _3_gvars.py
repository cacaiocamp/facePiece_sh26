from oscpy.client import OSCClient

# GENERAL CONTROL
clipsPlaying = False

# PRINT CONTROL
print_AllOSCMessages = False
print_AllThreadMessages = False

# interaction scores recordings
totalNumber_interactiveScores = 24
interactionScore_layer = 12
# interactionScores_possibleColumns = [2, 3, 4]
# interactionScores_possibleRecDurations = [2, 2, 2]
# interactionScores_possibleWaitDurations = [1, 1, 1]

interactionScores_possibleColumns = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
interactionScores_possibleRecDurations = [2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
interactionScores_possibleWaitDurations = [28, 28, 28, 34, 34, 34, 34, 34, 34, 34, 34, 34, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]

recording_count = 0
l_miniatureRecordings = []
l_availableRecordings = []
l_curAvailableLayers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
l_minRecordingsForPlayers = [1, 3, 7]

l_lastPerformancesRecordings = []
allowLastPerformancesRecordings = False

# resolume configuration
resolume_OSCIP = '192.168.43.54'
resolume_OSCPORT = 7000
resolume_OSCCLIENT = OSCClient(resolume_OSCIP, resolume_OSCPORT, encoding='utf8')
resolume_BASERESTURL = f"http://127.0.0.1:8080/api/v1"
resolume_recordingAvailable = True

# audienceLayers
audiencePlayers_possibleColumns = [[27, 28, 29], [31, 32, 33], [35, 36, 37]]
l_audiencePlayers = []
audienceLayersTotal = 9

curLayersUsed = [0, 0, 0]

# facePiece thread
facePieceThread = None
facePieceRunning = False
curFacePieceIndex = 9
l_possibleFacePieceColumns = [39, 40, 41, 42, 43, 44, 45, 46, 47, 48]
facePieceLayer = 11
facePieceDur = 980
facePieceNoClipColumn = 49
creditsDur = 21
creditsLayer = 10
creditsColumn = 50

# save/load recordings
RECORDINGS_SAVE_FILE = "recordings_save_file.txt"
saveWarningGiven = False
recordingsLoaded = False

allRecordingsSaved = True