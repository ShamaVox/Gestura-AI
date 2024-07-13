using UnityEngine;
using UnityEngine.Video;
using System.Collections;

public class AudioExtractor : MonoBehaviour
{
    public VideoPlayer videoPlayer;
    public AudioSource audioSource;

    public RenderTexture renderTexture;

    void Start()
    {
        // Set up VideoPlayer
        videoPlayer.audioOutputMode = VideoAudioOutputMode.AudioSource;
        videoPlayer.EnableAudioTrack(0, true);
        videoPlayer.SetTargetAudioSource(0, audioSource);

        // Set the render texture for video output
        videoPlayer.targetTexture = renderTexture;

        GameObject videoBackground = GameObject.CreatePrimitive(PrimitiveType.Quad);
        videoBackground.name = "VideoBackground";
        AdjustQuadToFullScreen(videoBackground);
        Material videoMaterial = new Material(Shader.Find("Standard"));
        videoMaterial.mainTexture = renderTexture;
        videoBackground.GetComponent<Renderer>().material = videoMaterial;

        // Play the video (this will also play the audio through the AudioSource)
        StartCoroutine(WaitAndPlayVideo());
    }

    IEnumerator WaitAndPlayVideo()
    {
        // Wait for 3 seconds
        yield return new WaitForSeconds(3);

        // Play the video (this will also play the audio through the AudioSource)
        videoPlayer.Play();
        Debug.Log("Video started playing with audio output to AudioSource.");
    }


   void AdjustQuadToFullScreen(GameObject quad)
    {
        Camera mainCamera = Camera.main;

        // Calculate the distance from the camera to the quad
        float quadDistance = Mathf.Abs(quad.transform.position.z - mainCamera.transform.position.z);

        // Get the screen aspect ratio
        float screenAspect = (float)Screen.width / (float)Screen.height;

        // Calculate the quad height and width based on the camera's field of view and the screen aspect ratio
        float quadHeight = 4.0f * quadDistance * Mathf.Tan(mainCamera.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float quadWidth = quadHeight * screenAspect;

        // Adjust the quad's scale
        quad.transform.localScale = new Vector3(quadWidth, quadHeight, 1);

        // Position the quad to be in front of the camera
        quad.transform.position = new Vector3(mainCamera.transform.position.x, mainCamera.transform.position.y, quadDistance);
    }
}

 
