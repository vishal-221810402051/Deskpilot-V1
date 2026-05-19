import win32com.client


class PowerPointController:
    """
    Handles PowerPoint context awareness and control.
    """

    def __init__(self):
        self.app = None

    def connect(self):
        try:
            self.app = win32com.client.GetActiveObject("PowerPoint.Application")
            return True
        except Exception:
            self.app = None
            return False

    def is_powerpoint_active(self) -> bool:
        return self.connect()

    def get_presentation_info(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            presentation = self.app.ActivePresentation

            total_slides = presentation.Slides.Count
            presentation_name = presentation.Name

            slideshow_active = False
            current_slide = None

            if self.app.SlideShowWindows.Count > 0:
                slideshow_active = True

                current_slide = (
                    self.app.SlideShowWindows(1)
                    .View.CurrentShowPosition
                )

            return {
                "status": "success",
                "presentation_name": presentation_name,
                "total_slides": total_slides,
                "slideshow_active": slideshow_active,
                "current_slide": current_slide,
            }

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }
