form Compute CPPS
    sentence wav_path
    sentence output_path
    sentence textgrid_path -
    real start_time 0
    real end_time 0
endform


segmentStart = start_time
segmentEnd = end_time


# If a TextGrid is provided, use the span between the first and the
# last labeled interval of tier 1.
# Empty intervals and pauses labeled as <p> are excluded.
if textgrid_path$ <> "-"
    Read from file: textgrid_path$
    tg = selected("TextGrid")

    numberOfIntervals = Get number of intervals: 1
    found = 0

    for intervalNumber from 1 to numberOfIntervals
        label$ = Get label of interval: 1, intervalNumber

        if label$ <> "" and label$ <> "<p>"
            intervalStart = Get start time of interval: 1, intervalNumber
            intervalEnd = Get end time of interval: 1, intervalNumber

            if found = 0
                segmentStart = intervalStart
                found = 1
            endif

            segmentEnd = intervalEnd
        endif
    endfor

    removeObject: tg
endif


Read from file: wav_path$
sound = selected("Sound")
duration = Get total duration


# Safety values so the interval stays within the audio.
if segmentStart < 0
    segmentStart = 0
endif

if segmentEnd <= segmentStart or segmentEnd > duration
    segmentEnd = duration
endif


# Extract only the segment that will be analyzed.
selectObject: sound
Extract part: segmentStart, segmentEnd, "rectangular", 1.0, "no"
segment = selected("Sound")


# Parameters from Murton, Hillman and Mehta (2020).
# PowerCepstrogram:
#   pitch floor = 60 Hz
#   time step = 0.002 s
#   maximum frequency = 5000 Hz
#   pre-emphasis from = 50 Hz
To PowerCepstrogram: 60, 0.002, 5000, 50
powerCepstrogram = selected("PowerCepstrogram")


# CPPS:
#   subtract trend before smoothing = no
#   time averaging window = 0.01 s
#   quefrency averaging window = 0.001 s
#   peak-search pitch range = 60-330 Hz
#   tolerance = 0.05
#   interpolation = Parabolic
#   trend-line quefrency range = 0.001-0 s (no upper limit)
#   trend type = Straight
#   fit method = Robust
cpps = Get CPPS: "no", 0.01, 0.001, 60, 330, 0.05, "Parabolic", 0.001, 0, "Straight", "Robust"


# Save a single CPPS value, expressed in dB.
writeFileLine: output_path$, fixed$(cpps, 6)


removeObject: powerCepstrogram, segment, sound
