using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;
// using System.Regex;
using System;

public class AutoAnimationController : MonoBehaviour
{
    public Animator animator;

    private Queue<string> animationQueue = new Queue<string>();
    private bool isPlayingAnimation = false;

    public Dictionary<string, List<string>> textToAnimationMap = new Dictionary<string, List<string>>
    {
        {"hello", new List<string>{"Hello"}},
        {"hi", new List<string>{"Hello"}},
        {"hey", new List<string>{"Hello"}},
        {"you are welcome", new List<string>{"YouAreWelcome"}},
        {"you're welcome", new List<string>{"YouAreWelcome"}},

        {"please", new List<string>{"Please"}},
        {"maybe", new List<string>{"Maybe"}},
        
        {"thanks", new List<string>{"ThankYou"}},
        {"thank you", new List<string>{"ThankYou"}},
        {"go", new List<string>{"Go"}},
        {"yes", new List<string>{"Yes"}},
        {"no", new List<string>{"No"}},
        {"come", new List<string>{"Come"}},
        {"look", new List<string>{"Look"}},
        {"talk", new List<string>{"Talk"}},

        {"one", new List<string>{"One"}},
        {"1", new List<string>{"One"}},
        {"two", new List<string>{"Two"}},
        {"2", new List<string>{"Two"}},
        {"three", new List<string>{"Three"}},
        {"3", new List<string>{"Three"}},
        {"four", new List<string>{"Four"}},
        {"4", new List<string>{"Four"}},
        {"five", new List<string>{"Five"}},
        {"5", new List<string>{"Five"}},
        {"six", new List<string>{"Six"}},
        {"6", new List<string>{"Six"}}
    };
    

    public void ProcessText(string text)
    {
        var time = System.DateTime.Now.ToString("HH:mm:ss.fff");
        Debug.Log($"{time} - Processing text: {text}");
        
        // Convert to lowercase and remove all punctuation
        text = Regex.Replace(text.ToLower(), @"[^\w\s]", "");

        var detectedPhrases = new List<(int index, string phrase, List<string> animations)>();

        foreach (var entry in textToAnimationMap)
        {
            var index = text.IndexOf(entry.Key, System.StringComparison.Ordinal);
            if (index != -1)
            {
                detectedPhrases.Add((index, entry.Key, entry.Value));
            }
        }
        
        time = System.DateTime.Now.ToString("HH:mm:ss.fff");
        Debug.Log($"{time} - Detected phrases: {string.Join(", ", detectedPhrases.Select(p => p.phrase))}");

        if (detectedPhrases.Count == 0) return; // Early exit if no phrases are detected

        detectedPhrases.Sort((a, b) => a.index.CompareTo(b.index)); // Sort by index

        foreach (var phrase in detectedPhrases)
        {
            foreach (var animation in phrase.animations)
            {
                QueueAnimation(animation);
            }
        }
    }

    public void QueueAnimation(string animationName)
    {
        var time = System.DateTime.Now.ToString("HH:mm:ss.fff");
        Debug.Log($"{time} - Queuing animation: {animationName}");
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

            // Wait until the animation state is set
            yield return new WaitUntil(() => animator.GetCurrentAnimatorStateInfo(0).IsName(animationName));
            
            var animationState = animator.GetCurrentAnimatorStateInfo(0);
            
            // Wait for the animation to finish
            yield return new WaitForSeconds(animationState.length);

            Debug.Log($"Finished playing animation: {animationName}");
        }

        isPlayingAnimation = false;
    }
}