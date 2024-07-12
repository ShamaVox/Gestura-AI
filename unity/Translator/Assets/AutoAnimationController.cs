using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using System.Linq;

public class AutoAnimationController : MonoBehaviour
{
    public Animator animator;

    private Queue<string> animationQueue = new Queue<string>();
    private bool isPlayingAnimation = false;

    private Dictionary<string, List<string>> textToAnimationMap = new Dictionary<string, List<string>>
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