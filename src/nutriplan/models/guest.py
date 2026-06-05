from nutriplan.models.schemas import DietStyle, HealthGoal, UserProfile


def guest_profile() -> UserProfile:
    """Default profile for chat when user has not saved onboarding yet."""
    return UserProfile(
        name="Guest",
        diet_style=DietStyle.VEGETARIAN,
        health_goal=HealthGoal.GENERAL_HEALTH,
        allergies=[],
        cuisine_preferences=["North Indian", "South Indian"],
    )