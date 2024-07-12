using UnityEngine;
using UnityEngine.UI;
using Whisper.Utils;
using Whisper;
using System.Collections.Generic;
using System.Collections;

public class MicrophoneStreamWithAnimation : MonoBehaviour
{
    public WhisperManager whisper;
    public MicrophoneRecord microphoneRecord;
    public Animator animator;

    [Header("UI")] 
    public Button button;
    public Text buttonText;
    public Text text;
    public ScrollRect scroll;
    private WhisperStream _stream;

    private Queue<string> animationQueue = new Queue<string>();
    private bool isPlayingAnimation = false;

    private Dictionary<string, string> textToAnimationMap = new Dictionary<string, string>
    {
        {"thank you", "ThankYou"},
        {"go", "Go"},
        {"one", "One"},
        {"1", "One"},
        {"three", "Three"},
        {"3", "Three"}
    };

    private async void Start()
    {
        _stream = await whisper.CreateStream(microphoneRecord);
        _stream.OnResultUpdated += OnResult;
        _stream.OnSegmentUpdated += OnSegmentUpdated;
        _stream.OnSegmentFinished += OnSegmentFinished;
        _stream.OnStreamFinished += OnFinished;

        microphoneRecord.OnRecordStop += OnRecordStop;
        button.onClick.AddListener(OnButtonPressed);
    }

    private void OnButtonPressed()
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
        text.text = result;
        UiUtils.ScrollDown(scroll);
        QueueAnimationsFromText(result);
    }
    
    private void OnSegmentUpdated(WhisperResult segment)
    {
        print($"Segment updated: {segment.Result}");
    }
    
    private void OnSegmentFinished(WhisperResult segment)
    {
        print($"Segment finished: {segment.Result}");
        QueueAnimationsFromText(segment.Result);
    }
    
    private void OnFinished(string finalResult)
    {
        print("Stream finished!");
    }

    private void QueueAnimationsFromText(string detectedText)
    {
        string lowerText = detectedText.ToLower();
        foreach (var pair in textToAnimationMap)
        {
            if (lowerText.Contains(pair.Key))
            {
                animationQueue.Enqueue(pair.Value);
            }
        }

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