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

    private HashSet<string> processedWords = new HashSet<string>();

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
            processedWords.Clear(); // Clear processed words when starting a new recording
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
    }
    
    private void OnSegmentFinished(WhisperResult segment)
    {
        var time = System.DateTime.Now.ToString("HH:mm:ss.fff");
        Debug.Log($"{time} - Segment finished: {segment.Result}");
        processedWords.Clear(); // Clear processed words when stream finishes
        // We don't need to process text here anymore as it's done in OnSegmentUpdated
    }

    private void OnSegmentUpdated(WhisperResult segment)
    {
        var time = System.DateTime.Now.ToString("HH:mm:ss.fff");
        Debug.Log($"{time} - Segment updated: {segment.Result}");
        
        // Process the updated segment
        string[] words = segment.Result.Split(new char[] { ' ', ',', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);
        foreach (string word in words)
        {
            string lowercaseWord = word.ToLower();
            if (!processedWords.Contains(lowercaseWord))
            {
                processedWords.Add(lowercaseWord);
                if (autoAnimationController.textToAnimationMap.ContainsKey(lowercaseWord))
                {
                    foreach (string animation in autoAnimationController.textToAnimationMap[lowercaseWord])
                    {
                        autoAnimationController.QueueAnimation(animation);
                    }
                }
            }
        }
    }
    
    private void OnFinished(string finalResult)
    {
        Debug.Log("Stream finished!");
        processedWords.Clear(); // Clear processed words when stream finishes
    }
}