using UnityEngine;
using UnityEngine.UI;
using Whisper.Utils;
using Whisper;
using System;

public class SpeechDetector : MonoBehaviour
{
    public WhisperManager whisper;
    public MicrophoneRecord microphoneRecord;
    public AutoAnimationController animationController;

    [Header("UI")]
    public Button recordButton;
    public Text buttonText;
    public Text transcriptionText;
    public ScrollRect scroll;

    private WhisperStream _stream;
    private string lastProcessedText = "";

    private async void Start()
    {
        _stream = await whisper.CreateStream(microphoneRecord);
        _stream.OnResultUpdated += OnResult;
        _stream.OnSegmentFinished += OnSegmentFinished;
        _stream.OnStreamFinished += OnFinished;

        microphoneRecord.OnRecordStop += OnRecordStop;
        recordButton.onClick.AddListener(OnRecordButtonPressed);
    }

    private void OnRecordButtonPressed()
    {
        if (!microphoneRecord.IsRecording)
        {
            _stream.StartStream();
            microphoneRecord.StartRecord();
            lastProcessedText = ""; // Reset the last processed text when starting a new recording
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
        transcriptionText.text = result;
        UiUtils.ScrollDown(scroll);
        ProcessNewText(result);
    }
    
    private void OnSegmentFinished(WhisperResult segment)
    {
        Debug.Log($"Segment finished: {segment.Result}");
        ProcessNewText(segment.Result);
    }
    
    private void OnFinished(string finalResult)
    {
        Debug.Log("Stream finished!");
        lastProcessedText = ""; // Reset the last processed text when the stream finishes
    }

    private void ProcessNewText(string detectedText)
    {
        if (string.IsNullOrEmpty(lastProcessedText))
        {
            lastProcessedText = detectedText;
            animationController.ProcessText(detectedText);
        }
        else if (detectedText.Length > lastProcessedText.Length)
        {
            string newText = detectedText.Substring(lastProcessedText.Length).Trim();
            lastProcessedText = detectedText;
            animationController.ProcessText(newText);
        }
    }
}