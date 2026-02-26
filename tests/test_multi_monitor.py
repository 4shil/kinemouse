"""Unit tests for MultiMonitorRouter."""

from kinemouse.utils.screen_info import ScreenInfo, Monitor
from kinemouse.utils.multi_monitor import MultiMonitorRouter


def make_dual_monitor() -> ScreenInfo:
    return ScreenInfo(
        primary=(1920, 1080),
        monitors=[
            Monitor(0, 0, 1920, 1080),
            Monitor(1920, 0, 1920, 1080),
        ]
    )


def test_virtual_resolution_dual():
    router = MultiMonitorRouter(make_dual_monitor())
    assert router.virtual_resolution == (3840, 1080)


def test_monitor_count():
    router = MultiMonitorRouter(make_dual_monitor())
    assert router.monitor_count() == 2


def test_map_center():
    router = MultiMonitorRouter(make_dual_monitor())
    x, y = router.map((0.5, 0.5), (0.0, 0.0, 1.0, 1.0))
    assert x == 1920
    assert y == 540


def test_which_monitor_first():
    router = MultiMonitorRouter(make_dual_monitor())
    mon = router.which_monitor(100, 100)
    assert mon.x == 0


def test_which_monitor_second():
    router = MultiMonitorRouter(make_dual_monitor())
    mon = router.which_monitor(2000, 100)
    assert mon.x == 1920
