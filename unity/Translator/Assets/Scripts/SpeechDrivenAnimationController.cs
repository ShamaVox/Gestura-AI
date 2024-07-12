using UnityEngine;
using UnityEngine.UI;
using Whisper.Utils;
using Whisper;
using System;
using System.Linq;
using System.Collections.Generic;
using System.Collections;

public class SpeechDrivenAnimationController : MonoBehaviour
{
    public WhisperManager whisper;
    public MicrophoneRecord microphoneRecord;
    public Animator animator;
    public Dropdown animationDropdown;

    [Header("UI")]
    public Button recordButton;
    public Text buttonText;
    public Text transcriptionText;
    public ScrollRect scroll;

    private WhisperStream _stream;
    private Queue<string> animationQueue = new Queue<string>();
    private bool isPlayingAnimation = false;
    private string lastProcessedText = "";

    public enum AnimationState
    {
        ThankYou,
        Go,
        One,
        Three,
        Yes,
        No,
        Come,
        Hello,
        YoureWelcome
    }

private Dictionary<string, string> textToAnimationMap = new Dictionary<string, string>
    {
        {"thank you", "ThankYou"},
        {"thanks", "ThankYou"},
        {"go", "Go"},
        {"one", "One"},
        {"1", "One"},
        {"three", "Three"},
        {"3", "Three"},
        {"yes", "Yes"},
        {"no", "No"},
        {"come", "Come"},
        {"hello", "Hello"},
        {"hi", "Hello"},
        {"youre welcome", "YoureWelcome"},
        {"you are welcome", "YoureWelcome"}
    };


    private async void Start()
    {
        SetupDropdown();
        _stream = await whisper.CreateStream(microphoneRecord);
        _stream.OnResultUpdated += OnResult;
        _stream.OnSegmentFinished += OnSegmentFinished;
        _stream.OnStreamFinished += OnFinished;

        microphoneRecord.OnRecordStop += OnRecordStop;
        recordButton.onClick.AddListener(OnRecordButtonPressed);
    }

    private void SetupDropdown()
    {
        animationDropdown.ClearOptions();
        string[] stateNames = Enum.GetNames(typeof(AnimationState));
        animationDropdown.AddOptions(stateNames.ToList());
        animationDropdown.onValueChanged.AddListener(OnDropdownValueChanged);
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
        QueueAnimationsFromText(result);
    }
    
    private void OnSegmentFinished(WhisperResult segment)
    {
        Debug.Log($"Segment finished: {segment.Result}");
        QueueAnimationsFromText(segment.Result);
    }
    
    private void OnFinished(string finalResult)
    {
        Debug.Log("Stream finished!");
        lastProcessedText = ""; // Reset the last processed text when the stream finishes
    }

    private void OnDropdownValueChanged(int index)
    {
        string selectedAnimation = animationDropdown.options[index].text;
        QueueAnimation(selectedAnimation);
    }

    private void QueueAnimationsFromText(string detectedText)
    {
        if (string.IsNullOrEmpty(lastProcessedText))
        {
            lastProcessedText = detectedText;
            ProcessFullText(detectedText);
        }
        else if (detectedText.Length > lastProcessedText.Length)
        {
            string newText = detectedText.Substring(lastProcessedText.Length).Trim();
            lastProcessedText = detectedText;
            ProcessFullText(newText);
        }
    }

    private void ProcessFullText(string text)
    {
        string[] words = text.ToLower().Split(new char[] { ' ', ',', '.', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);
        
        foreach (string word in words)
        {
            if (textToAnimationMap.TryGetValue(word, out string animationName))
            {
                QueueAnimation(animationName);
            }
        }
    }

    private void QueueAnimation(string animationName)
    {
        animationQueue.Enqueue(animationName);
        
        if (!isPlayingAnimation)
        {
            StartCoroutine(PlayQueuedAnimations());
        }
    }

    private IEnumerator PlayQueuedAnimations()
    {
        isPlayingAnimation = true;

        while (animationQueue.Count > 0)
        {
            string animationName = animationQueue.Dequeue();
            animator.Play(animationName);

            // Wait for the animation to finish
            yield return new WaitForSeconds(animator.GetCurrentAnimatorStateInfo(0).length);
            yield return new WaitForSeconds(0.1f); // Small buffer between animations
        }

        isPlayingAnimation = false;
    }
}