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
    public Animator animator;

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
        Come,
        Go,
        Look,
        Yes,
        No,
        ThankYou,
        Talk
    }

private Dictionary<string, List<string>> textToAnimationMap = new Dictionary<string, List<string>>
    {
        {"thank you", new List<string>{"ThankYou"}},
        {"thanks", new List<string>{"ThankYou"}},
        {"go", new List<string>{"Go"}},
        {"yes", new List<string>{"Yes"}},
        {"no", new List<string>{"No"}},
        {"come", new List<string>{"Come"}},
        {"look", new List<string>{"Look"}},
        {"talk", new List<string>{"Talk"}}
    };
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
        // Convert to lowercase and remove all punctuation
        text = Regex.Replace(text.ToLower(), @"[^\w\s]", "");

        List<(int index, string phrase, List<string> animations)> detectedPhrases = new List<(int, string, List<string>)>();

        foreach (var entry in textToAnimationMap)
        {
            string pattern = @"\b" + Regex.Escape(entry.Key) + @"\b";
            foreach (Match match in Regex.Matches(text, pattern))
            {
                detectedPhrases.Add((match.Index, entry.Key, entry.Value));
            }
        }

        // Sort detected phrases by their position in the text
        detectedPhrases.Sort((a, b) => a.index.CompareTo(b.index));

        foreach (var detected in detectedPhrases)
        {
            foreach (string animationName in detected.animations)
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