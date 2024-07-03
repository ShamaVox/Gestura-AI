using UnityEngine;
using UnityEngine.UIElements;
using System.Collections.Generic;

public class AnimationController : MonoBehaviour
{
    public UIDocument uiDocument;
    public Animator animator;
    public AnimationClip mainAnimationClip;

    private DropdownField animationDropdown;
    private Button playButton;

    private Dictionary<string, (float startTime, float duration)> animationData = new Dictionary<string, (float, float)>()
    {
        {"Look", (0f, 4f)},
        {"Thank You", (4f, 2f)},
        {"Yes", (7f, 4f)},
        {"No", (11f, 3f)},
        {"Go", (14f, 5f)},        
        
        {"Talk", (23f, 6f)},
        {"Come", (30f, 6f)},
        // {"Please", (10f, 1f)},
        // {"Maybe", (200f, 1f)},
        // {"You're Welcome", (2f, 1f)},
        // {"See", (5f, 0.75f)},
    };

    private bool isPlaying = false;
    private float animationEndTime;

    void OnEnable()
    {
        var root = uiDocument.rootVisualElement;
        
        animationDropdown = root.Q<DropdownField>("animation-dropdown");
        playButton = root.Q<Button>("play-button");

        animationDropdown.choices = new List<string>(animationData.Keys);
        playButton.clicked += PlaySelectedAnimation;

        // Ensure animation doesn't play automatically
        animator.enabled = false;
    }

    void Update()
    {
        if (isPlaying && Time.time >= animationEndTime)
        {
            StopAnimation();
        }
    }

    void PlaySelectedAnimation()
    {
        string selectedAnimation = animationDropdown.value;
        if (animationData.TryGetValue(selectedAnimation, out var animInfo))
        {
            float normalizedStartTime = animInfo.startTime / mainAnimationClip.length;
            
            animator.enabled = true;
            animator.Play("SignLanguageState", -1, normalizedStartTime);
            
            isPlaying = true;
            animationEndTime = Time.time + animInfo.duration;
        }
    }

    void StopAnimation()
    {
        animator.enabled = false;
        isPlaying = false;
    }
}