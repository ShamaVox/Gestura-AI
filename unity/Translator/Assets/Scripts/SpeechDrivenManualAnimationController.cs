using UnityEngine;
using UnityEngine.UI;
using Whisper.Utils;
using Whisper;
using System;
using System.Linq;
using System.Collections.Generic;
using System.Collections;
using System.Text.RegularExpressions;


public class SpeechDrivenManualAnimationController : MonoBehaviour
{
    public WhisperManager whisper;
    public MicrophoneRecord microphoneRecord;

    [Header("UI")]
    public Button recordButton;
    public Text buttonText;
    public Text transcriptionText;
    public ScrollRect scroll;

    private WhisperStream _stream;

    public AutoAnimationController autoAnimationController;

    private async void Start()
    {
        _stream = await whisper.CreateStream(microphoneRecord);
        _stream.OnResultUpdated += OnResult;
        _stream.OnSegmentFinished += OnSegmentFinished;
        _stream.OnStreamFinished += OnFinished;
        _stream.OnSegmentUpdated += OnSegmentUpdated;
        microphoneRecord.OnRecordStop += OnRecordStop;
        recordButton.onClick.AddListener(OnRecordButtonPressed);

        OnRecordButtonPressed();
    }

    private void OnRecordButtonPressed()
    {
        if (!microphoneRecord.IsRecording)
        {
            _stream.StartStream();
            microphoneRecord.StartRecord();
        }
        else
            microphoneRecord.StopRecord();
    
        buttonText.text = microphoneRecord.IsRecording ? "Stop" : "Record";
    }

    private void OnRecordStop(AudioChunk recordedAudio)
    {
        buttonText.text = "Record";
    }

    private void OnResult(string result)
    {
        // Replace instances of [BLANK_AUDIO] and [INAUDIBLE] with a blank space
        result = Regex.Replace(result, @"\[BLANK_AUDIO\]", "");
        result = Regex.Replace(result, @"\[INAUDIBLE\]", "");
        transcriptionText.text = result;
        // UiUtils.ScrollDown(scroll);
    }
    
    private void OnSegmentFinished(WhisperResult segment)
    {
        Debug.Log($"Segment finished: {segment.Result}");
        autoAnimationController.ProcessText(segment.Result);
    }

    private void OnSegmentUpdated(WhisperResult segment)
    {
        Debug.Log($"Segment updated: {segment.Result}");
        // autoAnimationController.ProcessText(segment.Result);
    }
    
    private void OnFinished(string finalResult)
    {
        Debug.Log("Stream finished!");
    }
}