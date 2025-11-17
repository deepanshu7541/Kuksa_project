def decide_target(speed, distance):
    """
    ADAS decision logic:
    speed = ego speed (m/s or km/h, doesn't matter for now)
    distance = gap to lead vehicle in meters, or None if no lead
    """

    SAFE_DISTANCE = 10.0   # meters
    CRITICAL_DISTANCE = 5.0

    if distance is None:
        # Lead car disappeared → keep current speed
        return speed, "NO_LEAD"

    if distance < CRITICAL_DISTANCE:
        # Too close → hard brake
        target = max(0, speed - 10)
        return target, "HARD_BRAKE"

    if distance < SAFE_DISTANCE:
        # Getting close → soft brake
        target = max(0, speed - 5)
        return target, "SOFT_BRAKE"

    # Safe distance → maintain or slightly accelerate
    return speed + 1, "ACCELERATE"