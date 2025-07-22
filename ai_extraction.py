"""
AI Entity Extraction & Enhancement for Unified Memory Store.
Phase 2.2: AI-powered content analysis and entity extraction.
"""

import hashlib
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from difflib import SequenceMatcher

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIExtractor:
    """AI-powered entity extraction and content enhancement."""
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize the AI extractor.
        
        Args:
            use_spacy: Whether to use spaCy for advanced NER (falls back to regex if unavailable)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = None
        
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except OSError:
                logger.warning("spaCy model not found, falling back to regex extraction")
                self.use_spacy = False
        
        # Common false positives for name extraction
        self.name_false_positives = {
            'React', 'Python', 'JavaScript', 'TypeScript', 'Docker', 'Kubernetes',
            'API', 'REST', 'GraphQL', 'WebSocket', 'Database', 'Frontend', 'Backend',
            'GitHub', 'AWS', 'Azure', 'GCP', 'PostgreSQL', 'MySQL', 'SQLite',
            'MongoDB', 'Redis', 'Node', 'Express', 'Django', 'Flask', 'FastAPI'
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract entities from text content.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted entities with type, name, and confidence
        """
        entities = []
        
        # Extract person names
        people = self._extract_people(text)
        entities.extend([{
            "type": "person", 
            "name": name, 
            "confidence": score
        } for name, score in people])
        
        # Extract technologies and projects
        technologies = self._extract_technologies(text)
        entities.extend([{
            "type": "technology", 
            "name": tech, 
            "confidence": score
        } for tech, score in technologies])
        
        # Extract file and code references
        files = self._extract_file_references(text)
        entities.extend([{
            "type": "file", 
            "name": file_path, 
            "confidence": score
        } for file_path, score in files])
        
        # Extract project mentions
        projects = self._extract_projects(text)
        entities.extend([{
            "type": "project", 
            "name": project, 
            "confidence": score
        } for project, score in projects])
        
        return entities
    
    def _extract_people(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names from text using spaCy or regex."""
        if self.use_spacy and self.nlp:
            return self._extract_people_spacy(text)
        else:
            return self._extract_people_regex(text)
    
    def _extract_people_spacy(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names using spaCy NER."""
        doc = self.nlp(text)
        people = []
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                if len(name.split()) <= 3 and name not in self.name_false_positives:
                    # spaCy confidence is typically high for NER
                    confidence = 0.9
                    people.append((name, confidence))
        
        return people
    
    def _extract_people_regex(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names using regex patterns."""
        # Pattern for capitalized names (2-3 words max)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b'
        potential_names = re.findall(name_pattern, text)
        
        validated_names = []
        for name in set(potential_names):
            if (name not in self.name_false_positives and 
                len(name.split()) <= 3 and 
                len(name) >= 2):
                # Simple confidence scoring
                confidence = 0.8 if len(name.split()) >= 2 else 0.6
                validated_names.append((name, confidence))
        
        return validated_names
    
    def _extract_technologies(self, text: str) -> List[Tuple[str, float]]:
        """Extract technology and framework mentions."""
        # Known technology patterns
        tech_patterns = [
            r'\b(React|Vue|Angular|JavaScript|TypeScript|Python|Java|Go|Rust|C\+\+|C#)\b',
            r'\b(PostgreSQL|MySQL|SQLite|MongoDB|Redis|Cassandra|Elasticsearch)\b',
            r'\b(Docker|Kubernetes|AWS|Azure|GCP|Heroku|Vercel|Netlify)\b',
            r'\b(API|REST|GraphQL|WebSocket|gRPC|SOAP)\b',
            r'\b(Node\.js|Express|Django|Flask|FastAPI|Spring|Laravel|Rails)\b',
            r'\b(Webpack|Vite|Babel|ESLint|Prettier|Jest|PyTest|Mocha)\b'
        ]
        
        technologies = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in set(matches):
                if isinstance(match, tuple):
                    match = match[0]  # From capture groups
                technologies.append((match, 0.9))
        
        return technologies
    
    def _extract_file_references(self, text: str) -> List[Tuple[str, float]]:
        """Extract file paths and code references."""
        # File path patterns
        patterns = [
            r'\b[\w\/\-\.]+\.(py|js|ts|jsx|tsx|java|go|rs|sql|md|txt|json|yaml|yml|xml|html|css)\b',
            r'\b[\w\/\-]+\/[\w\/\-]+\b',  # Directory paths
            r'\b[a-zA-Z_][a-zA-Z0-9_]*\.(function|method|class|component)\b',  # Code references
        ]
        
        files = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in set(matches):
                if isinstance(match, tuple):
                    match = match[0]
                # For file extensions, reconstruct the full filename
                if match in ['py', 'js', 'ts', 'jsx', 'tsx', 'java', 'go', 'rs', 'sql', 'md', 'txt', 'json', 'yaml', 'yml', 'xml', 'html', 'css']:
                    # Look for the actual filename with this extension
                    filename_pattern = rf'\b[\w\/\-\.]+\.{re.escape(match)}\b'
                    filename_matches = re.findall(filename_pattern, text, re.IGNORECASE)
                    for filename in filename_matches:
                        files.append((filename, 0.7))
                else:
                    files.append((match, 0.7))
        
        return files
    
    def _extract_projects(self, text: str) -> List[Tuple[str, float]]:
        """Extract project and application mentions."""
        project_patterns = [
            r'\b([A-Z][a-zA-Z0-9\-\_]*)\s+(project|app|application|system|service|platform)\b',
            r'\b(?:working on|developing|building)\s+([A-Z][a-zA-Z0-9\-\_]+)\b',
            r'\b([A-Z][a-zA-Z0-9\-\_]+)\s+(?:project|application)\b'
        ]
        
        projects = []
        for pattern in project_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in set(matches):
                if isinstance(match, tuple):
                    # Take the first captured group (the project name)
                    match = match[0]
                if match and len(match) > 2 and match.lower() not in ['the', 'project', 'application', 'system', 'service', 'platform']:
                    projects.append((match, 0.8))
        
        return projects
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract key topics and themes from content."""
        topics = []
        
        # Technical activity topics
        activity_patterns = [
            r'\b(debugging|development|testing|deployment|migration|refactoring|optimization)\b',
            r'\b(planning|design|architecture|review|analysis|research)\b',
            r'\b(meeting|discussion|standup|retrospective|sprint|planning)\b',
            r'\b(monitoring|logging|alerting|observability|performance)\b'
        ]
        
        # Domain topics  
        domain_patterns = [
            r'\b(database|API|frontend|backend|authentication|security|authorization)\b',
            r'\b(performance|scaling|load\s+balancing|caching|CDN)\b',
            r'\b(bug|feature|issue|problem|solution|fix|workaround)\b',
            r'\b(integration|deployment|CI\/CD|pipeline|automation)\b'
        ]
        
        for patterns in [activity_patterns, domain_patterns]:
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                topics.extend([m.lower() for m in matches])
        
        return list(set(topics))
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate concise summary for long content."""
        if len(content) <= max_length:
            return content
        
        # Simple extractive summarization
        sentences = self._split_sentences(content)
        
        if not sentences:
            return content[:max_length].strip() + "..."
        
        # Take first sentence and most important points
        summary = sentences[0]
        
        if len(summary) < max_length - 20:
            # Add key sentences that contain important keywords
            important_keywords = ['decided', 'concluded', 'action', 'next', 'issue', 'problem', 'solution', 'fix']
            
            for sentence in sentences[1:]:
                if any(keyword in sentence.lower() for keyword in important_keywords):
                    if len(summary + " " + sentence) <= max_length - 3:
                        summary += " " + sentence
                    else:
                        break
        
        # Ensure we don't exceed max length
        if len(summary) > max_length - 3:
            summary = summary[:max_length-3].rsplit(' ', 1)[0] + "..."
        
        return summary
    
    def extract_action_items(self, content: str) -> List[str]:
        """Extract action items and decisions from content."""
        action_patterns = [
            r'(?:need to|should|must|will|going to|plan to)\s+([^.!?]+)',
            r'(?:action item|todo|task):\s*([^.!?]+)',
            r'(?:decided to|concluded|agreed to)\s+([^.!?]+)',
            r'(?:next steps?|follow up):\s*([^.!?]+)',
            r'(?:TODO|FIXME|HACK):\s*([^.!?]+)'
        ]
        
        actions = []
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            actions.extend([match.strip() for match in matches if match.strip()])
        
        return list(set(actions))
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-1 hash of content for caching."""
        return hashlib.sha1(content.encode('utf-8')).hexdigest()


class EntityMatcher:
    """Match extracted entities against existing entities."""
    
    def __init__(self, memory_store):
        """Initialize with reference to memory store."""
        self.memory_store = memory_store
    
    def find_similar_entities(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match extracted entities against existing entities."""
        matches = []
        
        for candidate in candidates:
            # Search for existing entities with similar names
            existing = self.memory_store.search(
                candidate['name'], 
                filters={"type": candidate['type']},
                limit=3
            )
            
            best_match = None
            best_similarity = 0.0
            
            for entity in existing:
                # Calculate name similarity
                similarity = self._calculate_name_similarity(
                    candidate['name'], 
                    entity['name']
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = entity
            
            if best_similarity > 0.8:  # High similarity threshold
                matches.append({
                    **candidate,
                    'existing_id': best_match['id'],
                    'similarity': best_similarity,
                    'action': 'link'  # Link to existing
                })
            else:
                # No good match found, mark for creation
                matches.append({
                    **candidate,
                    'action': 'create'  # Create new entity
                })
        
        return matches
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between entity names."""
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Exact match
        if n1 == n2:
            return 1.0
        
        # Sequence similarity
        similarity = SequenceMatcher(None, n1, n2).ratio()
        
        # Boost for partial matches (first/last name)
        if any(part in n2 for part in n1.split()) or any(part in n1 for part in n2.split()):
            similarity = max(similarity, 0.7)
        
        return similarity


class ContentEnhancer:
    """Enhance content with AI-generated metadata."""
    
    def __init__(self, memory_store, extractor: AIExtractor, matcher: EntityMatcher):
        """Initialize with dependencies."""
        self.memory_store = memory_store
        self.extractor = extractor
        self.matcher = matcher
    
    def enhance_context(self, context) -> Dict[str, Any]:
        """Enhance context with AI-generated metadata."""
        # Calculate content hash for caching
        content_hash = self.extractor.calculate_content_hash(context.content)
        
        # Check if we already have extraction results
        if context.metadata.get('extract_hash') == content_hash:
            logger.info(f"Using cached extraction results for context {context.id}")
            return {
                'topics': context.topics,
                'summary': context.summary,
                'action_items': context.metadata.get('action_items', []),
                'extracted_entities': context.metadata.get('extracted_entities', [])
            }
        
        # Extract entities
        extracted_entities = self.extractor.extract_entities(context.content)
        
        # Match against existing entities
        entity_matches = self.matcher.find_similar_entities(extracted_entities)
        
        # Extract topics
        topics = self.extractor.extract_topics(context.content)
        
        # Generate summary if needed
        summary = None
        if len(context.content) > 300:
            summary = self.extractor.generate_summary(context.content)
        
        # Extract action items
        action_items = self.extractor.extract_action_items(context.content)
        
        return {
            'topics': topics,
            'summary': summary,
            'action_items': action_items,
            'extracted_entities': entity_matches,
            'extract_hash': content_hash
        }
    
    def create_content_relationships(self, content_id: str, 
                                   extracted_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create relationships between content and extracted entities."""
        relationships = []
        
        for entity_data in extracted_entities:
            if entity_data['action'] == 'link':
                # Create relationship to existing entity
                relation = {
                    'source_id': content_id,
                    'target_id': entity_data['existing_id'],
                    'relation_type': self._determine_relation_type(entity_data),
                    'strength': entity_data.get('confidence', 0.5),
                    'metadata': {
                        'auto_generated': True,
                        'extraction_confidence': entity_data.get('confidence', 0.5),
                        'similarity': entity_data.get('similarity', 0.0)
                    }
                }
                relationships.append(relation)
        
        return relationships
    
    def _determine_relation_type(self, entity_data: Dict[str, Any]) -> str:
        """Determine appropriate relationship type for extracted entity."""
        entity_type = entity_data['type']
        
        type_mapping = {
            'person': 'mentions',
            'technology': 'references',
            'file': 'references',
            'project': 'relates_to',
            'task': 'relates_to'
        }
        
        return type_mapping.get(entity_type, 'relates_to') 