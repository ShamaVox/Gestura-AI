using UnityEngine;
using UnityEngine.UI;
using System;
using System.Linq;

public class DynamicAnimationController : MonoBehaviour
{
    public Animator animator;
    public Dropdown animationDropdown;

    // Define your animation states here
    public enum AnimationState
    {
        ThankYou,
        Go,
        One,
        Three,
        Yes,
        Come
    }

    private void Start()
    {
        SetupDropdown();
    }

    private void SetupDropdown()
    {
        // Clear any existing options
        animationDropdown.ClearOptions();

        // Get all animation state names
        string[] stateNames = Enum.GetNames(typeof(AnimationState));

        // Add animation states to dropdown
        animationDropdown.AddOptions(stateNames.ToList());

        // Add listener for when a dropdown item is selected
        animationDropdown.onValueChanged.AddListener(OnDropdownValueChanged);
    }

    private void OnDropdownValueChanged(int index)
    {
        // Get the selected animation state name
        string selectedAnimation = animationDropdown.options[index].text;

        // Play the selected animation
        PlayAnimation(selectedAnimation);
    }

    private void PlayAnimation(string stateName)
    {
        // Directly play the state
        animator.Play(stateName);
    }
}