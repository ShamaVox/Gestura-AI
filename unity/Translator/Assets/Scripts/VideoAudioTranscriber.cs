using UnityEngine;
using UnityEngine.Video;
using System.Collections;
using System.Threading.Tasks;
using Whisper;
using Whisper.Utils;
using System.Collections.Generic;
using System.Linq;
using UnityEngine.UI;
using System.Text.RegularExpressions;


[RequireComponent(typeof(AudioSource))]
public class VideoAudioTranscriber : MonoBehaviour
{
    public WhisperManager whisper;
    public AudioSource audioSource;

    [Header("UI")]
    public Button button;
    public Text buttonText;
    public Text text;
    public ScrollRect scroll;

    private WhisperStream _stream;
    private bool isStreaming = false;
    private int sampleRate;
    private int channels;
    private List<float> audioBuffer = new List<float>();

    public AutoAnimationController autoAnimationController = null;
    public bool startTranscriberOnStart = true;

    private async void Start()
    {
        // Initialize Whisper stream with the appropriate sample rate and channel count
        sampleRate = AudioSettings.outputSampleRate;
        channels = audioSource.spatialBlend == 0 ? 2 : 1; // Assuming stereo if spatial blend is zero

        _stream = await whisper.CreateStream(sampleRate, channels);
        _stream.OnResultUpdated += OnResult;
        _stream.OnSegmentUpdated += OnSegmentUpdated;
        _stream.OnSegmentFinished += OnSegmentFinished;
        _stream.OnStreamFinished += OnFinished;

        button.onClick.AddListener(OnButtonPressed);

        Debug.Log("VideoAudioTranscriber started.");

        if (startTranscriberOnStart) {
            OnButtonPressed();
        }
    }

    private void OnAudioFilterRead(float[] data, int channels)
    {
        if (isStreaming)
        {
            lock (audioBuffer)
            {
                audioBuffer.AddRange(data);
            }
        }
    }

    private void Update()
    {
        if (isStreaming)
        {
            lock (audioBuffer)
            {
                if (audioBuffer.Count > 0)
                {
                    // Process smaller chunks of audio data to reduce lag
                    int chunkSize = 512; // Adjust chunk size as needed
                    while (audioBuffer.Count >= chunkSize)
                    {
                        float[] chunkData = audioBuffer.Take(chunkSize).ToArray();
                        audioBuffer.RemoveRange(0, chunkSize);

                        AudioChunk chunk = new AudioChunk
                        {
                            Data = chunkData,
                            Frequency = sampleRate,
                            Channels = channels,
                            Length = chunkSize / (float)(sampleRate * channels),
                            IsVoiceDetected = true // For simplicity, assume voice is detected. Implement VAD as needed.
                        };

                        _stream.AddToStream(chunk);
                    }
                }
            }
        }
    }

    private void OnButtonPressed()
    {
        if (!isStreaming)
        {
            _stream.StartStream();
            isStreaming = true;
            buttonText.text = "Stop";
            Debug.Log("Started streaming.");
        }
        else
        {
            _stream.StopStream();
            isStreaming = false;
            buttonText.text = "Record";
            Debug.Log("Stopped streaming.");
        }
    }

    private void OnResult(string result)
    {
        result = Regex.Replace(result, @"\[BLANK_AUDIO\]", "");
        result = Regex.Replace(result, @"\[INAUDIBLE\]", "");
        text.text = result;
        //UiUtils.ScrollDown(scroll);
    }

    private void OnSegmentUpdated(WhisperResult segment)
    {
        Debug.Log($"Segment updated: {segment.Result}");
        if (autoAnimationController != null)
        {
            autoAnimationController.ProcessText(segment.Result);
        }
    }

    private void OnSegmentFinished(WhisperResult segment)
    {
        Debug.Log($"Segment finished: {segment.Result}");
        
    }

    private void OnFinished(string finalResult)
    {
        Debug.Log("Stream finished!");
    }
}