// using UnityEngine;
// using UnityEngine.UI;
// using UnityEngine.Video;
// using Whisper;
// using Whisper.Utils;
// using System.Collections.Generic;
// using System.Threading.Tasks;
// using System.Collections;
// using UnityEngine.Experimental.Video;

// public class VideoPlayerWithAudioExtraction : MonoBehaviour
// {
//     public WhisperManager manager;
//     public VideoPlayer videoPlayer;
//     public RawImage videoDisplay;
//     public Button playButton;
//     public Text playButtonText;
//     public Text outputText;
//     public Text timeText;
//     public ScrollRect scroll;

//     private bool isPlaying = false;
//     private WhisperStream _stream;
//     private string _buffer = "";

//     private void Start()
//     {
//         playButton.onClick.AddListener(TogglePlayback);
//         InitializeWhisperStream();
//         SetupVideoPlayer();
//     }

//     private void InitializeWhisperStream()
//     {
//         var streamParams = new WhisperStreamParams(
//             manager.defaultParams,
//             (int)AudioSettings.outputSampleRate,
//             2,  // Assuming stereo audio
//             stepSec: 1f,
//             keepSec: 0.2f,
//             lengthSec: 5f
//         );

//         _stream = new WhisperStream(manager.whisper, streamParams);
//         _stream.OnSegmentUpdated += OnSegmentUpdated;
//         _stream.OnStreamFinished += OnStreamFinished;
//     }

//     private void SetupVideoPlayer()
//     {
//         videoPlayer.prepareCompleted += OnVideoPrepared;
//         videoPlayer.audioOutputMode = VideoAudioOutputMode.AudioSource;
//         videoPlayer.EnableAudioTrack(0, true);
//         videoPlayer.Prepare();
//     }

//     private void OnVideoPrepared(VideoPlayer source)
//     {
//         videoDisplay.texture = source.texture;
//     }

//     private void TogglePlayback()
//     {
//         if (isPlaying)
//         {
//             StopPlayback();
//         }
//         else
//         {
//             StartPlayback();
//         }
//     }

//     private void StartPlayback()
//     {
//         isPlaying = true;
//         playButtonText.text = "Stop";
//         videoPlayer.Play();
//         _stream.StartStream();
//         StartCoroutine(CaptureAudio());
//     }

//     private void StopPlayback()
//     {
//         isPlaying = false;
//         playButtonText.text = "Play";
//         videoPlayer.Pause();
//         _stream.StopStream();
//         StopAllCoroutines();
//     }

//     private IEnumerator CaptureAudio()
//     {
//         while (isPlaying)
//         {
//             float[] samples = new float[1024];
//             videoPlayer.GetTargetAudioSource(0).GetOutputData(samples, 0);


//             var chunk = new AudioChunk(samples, 48000, 2, 0.5f);
//             _stream.AddToStream(chunk);

//             yield return new WaitForSeconds(0.05f);  // Adjust this value as needed
//         }
//     }

//     private void OnSegmentUpdated(WhisperResult segment)
//     {
//         _buffer += segment.Result;
//         outputText.text = _buffer;
//         UiUtils.ScrollDown(scroll);
//     }

//     private void OnStreamFinished(string finalResult)
//     {
//         Debug.Log("Transcription finished: " + finalResult);
//         timeText.text = $"Video duration: {videoPlayer.length:F2} seconds";
//     }
// }