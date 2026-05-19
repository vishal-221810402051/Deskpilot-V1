import pythoncom
import win32com.client


class PowerPointController:
    """
    Handles PowerPoint context awareness and slide control.
    """

    def __init__(self):
        self.app = None

    def connect(self) -> bool:
        try:
            pythoncom.CoInitialize()

            self.app = win32com.client.GetActiveObject("PowerPoint.Application")
            return True

        except Exception:
            try:
                self.app = win32com.client.Dispatch("PowerPoint.Application")
                self.app.Visible = True
                return True

            except Exception:
                self.app = None
                return False

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

    def start_slideshow(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            presentation = self.app.ActivePresentation
            presentation.SlideShowSettings.Run()

            return {
                "status": "success",
                "message": "Started slideshow",
            }

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def end_slideshow(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            if self.app.SlideShowWindows.Count == 0:
                return {
                    "status": "error",
                    "message": "No active slideshow",
                }

            self.app.SlideShowWindows(1).View.Exit()

            return {
                "status": "success",
                "message": "Ended slideshow",
            }

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def next_slide(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            if self.app.SlideShowWindows.Count == 0:
                return {
                    "status": "error",
                    "message": "No active slideshow",
                }

            view = self.app.SlideShowWindows(1).View
            view.Next()

            return self.get_presentation_info()

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def previous_slide(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            if self.app.SlideShowWindows.Count == 0:
                return {
                    "status": "error",
                    "message": "No active slideshow",
                }

            view = self.app.SlideShowWindows(1).View
            view.Previous()

            return self.get_presentation_info()

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def go_to_slide(self, slide_number: int) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            presentation = self.app.ActivePresentation
            total_slides = presentation.Slides.Count

            if slide_number < 1 or slide_number > total_slides:
                return {
                    "status": "error",
                    "message": f"Slide {slide_number} is outside range 1-{total_slides}",
                }

            if self.app.SlideShowWindows.Count == 0:
                presentation.SlideShowSettings.Run()

            view = self.app.SlideShowWindows(1).View
            view.GotoSlide(slide_number)

            return self.get_presentation_info()

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }

    def go_to_first_slide(self) -> dict:
        return self.go_to_slide(1)

    def go_to_last_slide(self) -> dict:
        if not self.connect():
            return {
                "status": "error",
                "message": "PowerPoint is not active",
            }

        try:
            total_slides = self.app.ActivePresentation.Slides.Count
            return self.go_to_slide(total_slides)

        except Exception as error:
            return {
                "status": "error",
                "message": str(error),
            }
