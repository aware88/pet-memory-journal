import os
import string
import unicodedata
import json
from collections import defaultdict

class TranscriptAnalyzer:
    def __init__(self, transcripts_dir="transcripts"):
        self.transcripts_dir = transcripts_dir
        self.allowed_chars = set(string.printable)  # ASCII printable characters
        self.analysis_results = {}

    def analyze_file(self, filename):
        filepath = os.path.join(self.transcripts_dir, filename)
        result = {
            'total_chars': 0,
            'non_ascii_chars': defaultdict(int),
            'non_ascii_positions': [],
            'special_chars': defaultdict(int),
            'is_ascii_compatible': True,
            'suggested_fixes': []
        }

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                result['total_chars'] = len(content)
                
                for pos, char in enumerate(content):
                    # Check for non-ASCII characters
                    if ord(char) > 127:
                        result['is_ascii_compatible'] = False
                        result['non_ascii_chars'][char] += 1
                        result['non_ascii_positions'].append({
                            'position': pos,
                            'char': char,
                            'context': content[max(0, pos-20):min(len(content), pos+20)]
                        })
                        
                        # Get the ASCII equivalent if possible
                        ascii_version = unicodedata.normalize('NFKD', char).encode('ASCII', 'ignore').decode()
                        if ascii_version:
                            result['suggested_fixes'].append({
                                'original': char,
                                'suggested': ascii_version
                            })
                    
                    # Check for special characters
                    elif char not in string.ascii_letters + string.digits + ' ':
                        result['special_chars'][char] += 1

        except Exception as e:
            result['error'] = str(e)

        return result

    def analyze_all_transcripts(self):
        print("\nAnalyzing transcripts for ASCII compatibility...")
        
        for filename in os.listdir(self.transcripts_dir):
            if filename.endswith('.txt'):
                print(f"\nAnalyzing: {filename}")
                result = self.analyze_file(filename)
                self.analysis_results[filename] = result
                
                # Print summary for this file
                print(f"Total characters: {result['total_chars']}")
                print(f"ASCII compatible: {'Yes' if result['is_ascii_compatible'] else 'No'}")
                
                if not result['is_ascii_compatible']:
                    print("\nNon-ASCII characters found:")
                    for char, count in result['non_ascii_chars'].items():
                        print(f"'{char}' (occurs {count} times)")
                        
                    print("\nSample contexts:")
                    for pos in result['non_ascii_positions'][:3]:  # Show first 3 examples
                        print(f"...{pos['context']}...")
                        
                    if result['suggested_fixes']:
                        print("\nSuggested replacements:")
                        for fix in result['suggested_fixes']:
                            print(f"Replace '{fix['original']}' with '{fix['suggested']}'")

    def generate_clean_version(self, filename):
        """Generate an ASCII-compatible version of the transcript"""
        filepath = os.path.join(self.transcripts_dir, filename)
        clean_filepath = os.path.join(self.transcripts_dir, f"ascii_{filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to ASCII
            ascii_content = unicodedata.normalize('NFKD', content).encode('ASCII', 'ignore').decode()
            
            # Save ASCII version
            with open(clean_filepath, 'w', encoding='ascii') as f:
                f.write(ascii_content)
            
            return clean_filepath
        except Exception as e:
            print(f"Error generating clean version: {e}")
            return None

    def save_analysis_report(self):
        """Save the analysis results to a JSON file"""
        report_path = os.path.join(self.transcripts_dir, 'transcript_analysis_report.json')
        
        # Convert defaultdict to regular dict for JSON serialization
        serializable_results = {}
        for filename, result in self.analysis_results.items():
            serializable_results[filename] = {
                'total_chars': result['total_chars'],
                'non_ascii_chars': dict(result['non_ascii_chars']),
                'special_chars': dict(result['special_chars']),
                'is_ascii_compatible': result['is_ascii_compatible'],
                'suggested_fixes': result['suggested_fixes']
            }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed analysis report saved to: {report_path}")

    def create_ascii_versions(self):
        """Create ASCII-compatible versions of all transcripts"""
        print("\nCreating ASCII-compatible versions of transcripts...")
        
        for filename in os.listdir(self.transcripts_dir):
            if filename.endswith('.txt') and not filename.startswith('ascii_'):
                print(f"Processing: {filename}")
                clean_file = self.generate_clean_version(filename)
                if clean_file:
                    print(f"Created ASCII version: {os.path.basename(clean_file)}")

if __name__ == "__main__":
    analyzer = TranscriptAnalyzer()
    analyzer.analyze_all_transcripts()
    analyzer.save_analysis_report()
    analyzer.create_ascii_versions() 