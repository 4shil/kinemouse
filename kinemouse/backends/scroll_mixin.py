"""
ScrollMixin — adds scroll() capability to any OS backend.
Mix this into platform-specific backends that support scrolling.

Usage:
    class LinuxX11Backend(BaseBackend, ScrollMixin):
        ...
    backend.scroll(ScrollDirection.UP, magnitude=2)
"""

from kinemouse.state.scroll_gesture import ScrollDirection


class ScrollMixin:
    """
    Mixin that implements scroll dispatch via the backend's native scroll method.
    Subclasses must implement _scroll_up(magnitude) and _scroll_down(magnitude).
    """

    def scroll(self, direction: ScrollDirection, magnitude: int = 1):
        if direction == ScrollDirection.UP:
            self._scroll_up(magnitude)
        else:
            self._scroll_down(magnitude)

    def _scroll_up(self, magnitude: int):
        raise NotImplementedError

    def _scroll_down(self, magnitude: int):
        raise NotImplementedError
