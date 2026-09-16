from pathlib import Path
import re

path = Path('lib/widgets/viewer/visual/entry_page_view.dart')
text = path.read_text()

if '_buildObjectNotesViewportOverlay' in text:
    print('ObjectNote overlay fix already applied')
    raise SystemExit(0)

overlay = '''  Widget _buildObjectNotesViewportOverlay() {
    return Positioned.fill(
      child: IgnorePointer(
        child: StreamBuilder<MagnifierState>(
          stream: _magnifierController.stateStream,
          initialData: _magnifierController.currentState,
          builder: (context, snapshot) {
            final boundaries = _magnifierController.scaleBoundaries;
            final state = snapshot.data;
            if (boundaries == null || state == null || state.scale == null || _objectNotes.isEmpty) {
              return const SizedBox.shrink();
            }

            final scale = state.scale!;
            final viewportCenter = boundaries.viewportCenter;
            final contentCenter = boundaries.contentSize.center(Offset.zero);
            final contentSize = boundaries.contentSize;

            return Stack(
              clipBehavior: Clip.none,
              children: [
                for (final note in _objectNotes)
                  Builder(
                    builder: (context) {
                      final contentPosition = Offset(
                        note.x * contentSize.width,
                        note.y * contentSize.height,
                      );
                      final viewportPosition = viewportCenter +
                          state.position +
                          (contentPosition - contentCenter) * scale;

                      return Positioned(
                        left: viewportPosition.dx - 14,
                        top: viewportPosition.dy - 14,
                        child: Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: Colors.red,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                          ),
                          alignment: Alignment.center,
                          child: const Text(
                            '•',
                            style: TextStyle(color: Colors.white, fontSize: 18, height: 1),
                          ),
                        ),
                      );
                    },
                  ),
              ],
            );
          },
        ),
      ),
    );
  }

'''

text, n = re.subn(
    r'  Widget _buildObjectNotesOverlay\(\) \{.*?(?=  Widget _buildRasterView\(\) \{)',
    lambda m: overlay,
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError('ObjectNote overlay method not found')

raster = '''  Widget _buildRasterView() {
    return _buildMagnifier(
      applyScale: false,
      child: RasterImageView(
        entry: entry,
        viewStateNotifier: _viewStateNotifier,
        errorBuilder: (context, error, stackTrace) => ErrorView(entry: entry, onTap: _onTap),
      ),
    );
  }

'''
text, n = re.subn(
    r'  Widget _buildRasterView\(\) \{.*?(?=  Widget _buildSvgView\(\) \{)',
    lambda m: raster,
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError('Raster view method not found')

svg = '''  Widget _buildSvgView() {
    return _buildMagnifier(
      maxScale: EntryPageView.vectorMaxScale,
      scaleStateCycle: _vectorScaleStateCycle,
      applyScale: false,
      child: VectorImageView(
        entry: entry,
        viewStateNotifier: _viewStateNotifier,
        errorBuilder: (context, error, stackTrace) => ErrorView(entry: entry, onTap: _onTap),
      ),
    );
  }

'''
text, n = re.subn(
    r'  Widget _buildSvgView\(\) \{.*?(?=  Widget _buildVideoView\(\) \{)',
    lambda m: svg,
    text,
    count=1,
    flags=re.S,
)
if n != 1:
    raise RuntimeError('SVG view method not found')

marker = '    if (!settings.viewerUseCutout) {'
insertion = '''    if (_objectNotes.isNotEmpty) {
      child = Stack(
        children: [
          child,
          _buildObjectNotesViewportOverlay(),
        ],
      );
    }

'''
if marker not in text:
    raise RuntimeError('Build insertion point not found')
text = text.replace(marker, insertion + marker, 1)

path.write_text(text)
print('ObjectNote overlay patched outside AvesMagnifier')
