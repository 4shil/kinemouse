# KineMouse Changelog

## Version 1.0.0 (MVP — 2026-02-25)

### Core Features
- ✅ Cross-platform gesture mouse (Windows, macOS, Linux X11/Wayland)
- ✅ 3-layer architecture (Vision → State Machine → OS Backends)
- ✅ Hand gesture recognition via MediaPipe
- ✅ Dynamic threshold normalization (D_ref)
- ✅ EMA smoothing for stable cursor movement
- ✅ Double-pinch state machine for click/drag detection
- ✅ Right-click via Thumb + Middle pinch
- ✅ 30 FPS async OS dispatch for zero-latency feel
- ✅ Platform auto-detection and graceful fallback
- ✅ First-run permission checks and guidance
- ✅ Comprehensive unit tests (pytest)
- ✅ Full documentation and architecture diagrams

### Technical Highlights
- Decoupled Layer 1 (vision) from Layer 3 (OS control)
- BaseBackend interface for pluggable OS adapters
- Event-driven architecture via MouseEvent dataclass
- Thread-safe async dispatcher queue
- Wayland uinput kernel-level mouse device
- macOS Quartz integration
- Windows DirectInput fallback support

### Known Limitations (Phase 2)
- Single-monitor only (multi-monitor support planned)
- No GUI dashboard yet (Tkinter/PyQt coming)
- Scroll/zoom gestures not implemented
- No gesture customization UI
- Camera index hardcoded (CLI arg coming)

### Performance
- Target CPU: < 10% on quad-core processor
- Latency: < 33ms (30 FPS)
- Memory: ~150MB base + MediaPipe cache

## Future Roadmap

### Phase 2
- Multi-monitor cursor tracking
- Scroll & zoom gestures (Ring finger)
- Tkinter/PyQt GUI dashboard
- Sensitivity/smoothing tuning UI
- Custom gesture mapping

### Phase 3
- Hand pose-based gestures (thumbs up, peace sign, etc.)
- Voice command integration
- Gesture recording & replay
- Analytics dashboard
