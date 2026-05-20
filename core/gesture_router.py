class GestureRouter:
    """
    Maps gesture events to DeskPilot intents.
    Hardware later will send these same gesture names.
    """

    def gesture_to_intent(self, gesture: str) -> dict:
        mapping = {
            "swipe_right_to_left": {
                "action": "ppt_next_slide",
                "target": None,
                "source": "gesture",
            },
            "swipe_left_to_right": {
                "action": "ppt_previous_slide",
                "target": None,
                "source": "gesture",
            },
            "swipe_up": {
                "action": "ppt_start_slideshow",
                "target": None,
                "source": "gesture",
            },
            "swipe_down": {
                "action": "ppt_end_slideshow",
                "target": None,
                "source": "gesture",
            },
            "twist_clockwise": {
                "action": "window_maximize_active",
                "target": None,
                "source": "gesture",
            },
            "twist_anticlockwise": {
                "action": "window_minimize_active",
                "target": None,
                "source": "gesture",
            },
            "double_tap": {
                "action": "window_bring_front",
                "target": "powerpoint",
                "source": "gesture",
            },
        }

        return mapping.get(
            gesture,
            {
                "action": "unknown",
                "target": gesture,
                "source": "gesture",
            },
        )
