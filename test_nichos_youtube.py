import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(repo_root))

# Test the new analyzer
import importlib.util
spec = importlib.util.spec_from_file_location("nichos_youtube", str(repo_root / 'proyecto_youtube' / 'nichos_youtube.py'))
nichos_youtube = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nichos_youtube)
# Use the loaded module object directly
NicheAnalyzerYouTube = nichos_youtube.NicheAnalyzerYouTube

def test_analyzer():
    try:
        analyzer = NicheAnalyzerYouTube()
        # Disable actual API calls for testing
        analyzer.youtube = None
        
        # Test automatizable analysis with mock data
        mock_videos = [
            {'snippet': {'title': 'Tutorial: Cómo hacer un script', 'description': 'Paso a paso automatización', 'tags': ['tutorial','script'], 'channelId': 'UC123'}},
            {'snippet': {'title': 'Review del mejor producto', 'description': 'Análisis completo', 'tags': ['review'], 'channelId': 'UC456'}},
        ]
        
        result = analyzer.analyze_automatizable_advanced(mock_videos, 'ES')
        print('Test automatizable analysis:')
        print(f'Status: {result["automatizable_status"]}')
        print(f'Ratio: {result["automatizable_ratio"]}')
        print(f'Signals: {result["automatizable_signals"]}')
        
        # Test channel analysis
        channel_result = analyzer.analyze_channel_sizes(mock_videos)
        print('\nTest channel analysis:')
        print(f'Small channels: {channel_result["small_channels_ratio"]}%')
        print(f'Medium channels: {channel_result["medium_channels_ratio"]}%')
        print(f'Large channels: {channel_result["large_channels_ratio"]}%')
        
        print('\nTest successful! ✅')
        
    except Exception as e:
        print(f'Test failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_analyzer()
