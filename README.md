# facePiece_sh26
[facePiece](https://eucaio.art/en/comps.html#g?#activateContentFacePiece) Python script developed for integration with Resolume Arena. Besides playing facePiece iterations with different performer configurations, it also: (1) plays a video score in a separate monitor; (2) records the audience member performing this score; (3) displays audience members recorded performances in the video screen as a pre-show for facePiece. It was developed specifically for facePiece performance at YOUNG Theatre, Shanghai, in the [GOAT Festival 2026](https://mp.weixin.qq.com/s/Uj57F83aQdfuRN-R69NqVw).

The structure of Resolume Patch is:
- a layer with a series of different 4k renders of facePiece, with different performers and position combinations. This video is outputted to a single 4k channel, mapping the videos accordingly to the 15x3 meters LED Wall present in the space;
- a layer with a series of 1080p video scores, from 2 to 6 seconds long, mapped to another output of the same computer;
- 9 layers and three columns for the video recordings of audience, routed to different parts of the LED Wall, controlled through REST API/Webserver messages;
- a layer for receiving the live-image from a camera, routed to the recording setup of Resolume, recording vertical 1080p DXV videos.

The script communicates with Resolume using both OSC messages and REST API. The OSC messages basically control the timing, start and end of each recording, and also which iteration of facePiece it is supposed to play. REST API messages control the clearing, setting recorded videos as clips and playing of the clips, in something like a "circular buffer". At the end of each iteration, the code clears the last played column for the videos; plays the next one; and sets the videos to be played after it.

In total, 74 audience members face performances videos were recorded.

More information about the piece and this performance of it can be found at [eucaio.art](https://eucaio.art).