using UnityEngine;
using UnityEngine.Video;

public class VideoSetup : MonoBehaviour
{
    public VideoPlayer videoPlayer;
    public AudioSource audioSource;
    public RenderTexture renderTexture;
    public GameObject avatar;

    void Start()
    {
        // Set up VideoPlayer
        videoPlayer.audioOutputMode = VideoAudioOutputMode.AudioSource;
        videoPlayer.EnableAudioTrack(0, true);
        videoPlayer.SetTargetAudioSource(0, audioSource);
        videoPlayer.targetTexture = renderTexture;

        // Create a Quad for the video background
        GameObject videoBackground = GameObject.CreatePrimitive(PrimitiveType.Quad);
        videoBackground.name = "VideoBackground";

        // Adjust the Quad to fill the camera view
        AdjustQuadToFullScreen(videoBackground);

        // Create and assign the video material
        Material videoMaterial = new Material(Shader.Find("Standard"));
        videoMaterial.mainTexture = renderTexture;
        videoBackground.GetComponent<Renderer>().material = videoMaterial;

        // Position the avatar
        if (avatar != null)
        {
            avatar.transform.position = new Vector3(0, 0, -2); // Position in front of the video background
        }

        // Play the video
        videoPlayer.Play();
    }

    void AdjustQuadToFullScreen(GameObject quad)
    {
        Camera mainCamera = Camera.main;

        // Calculate the distance from the camera to the quad
        float quadDistance = (quad.transform.position - mainCamera.transform.position).z;

        // Calculate the height and width of the quad based on the camera's field of view and aspect ratio
        float quadHeight = 2.0f * quadDistance * Mathf.Tan(mainCamera.fieldOfView * 0.5f * Mathf.Deg2Rad);
        float quadWidth = quadHeight * mainCamera.aspect;

        // Adjust the quad's scale
        quad.transform.localScale = new Vector3(quadWidth, quadHeight, 1);

        // Position the quad to be in front of the camera
        quad.transform.position = new Vector3(mainCamera.transform.position.x, mainCamera.transform.position.y, quadDistance);
    }
}
