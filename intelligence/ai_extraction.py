"""
AI Entity Extraction & Enhancement for Unified Memory Store.
Phase 2.2: AI-powered content analysis and entity extraction.
"""

import hashlib
import logging
import re
import subprocess
import sys
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
    
    def __init__(self, use_spacy: bool = True, spacy_model: str = "en_core_web_lg"):
        """
        Initialize the AI extractor.
        
        Args:
            use_spacy: Whether to use spaCy for advanced NER (falls back to regex if unavailable)
            spacy_model: spaCy model to use (en_core_web_sm, en_core_web_md, en_core_web_lg)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.spacy_model = spacy_model
        self.nlp = None
        
        if self.use_spacy:
            try:
                self.nlp = spacy.load(self.spacy_model)
                logger.info(f"spaCy model '{self.spacy_model}' loaded successfully")
            except OSError:
                logger.warning(f"spaCy model '{self.spacy_model}' not found, attempting to download with uv...")
                if self._download_spacy_model():
                    try:
                        self.nlp = spacy.load(self.spacy_model)
                        logger.info(f"spaCy model '{self.spacy_model}' downloaded and loaded successfully")
                    except OSError:
                        logger.warning(f"Failed to load spaCy model '{self.spacy_model}' after download, falling back to regex extraction")
                        self.use_spacy = False
                else:
                    logger.warning(f"Failed to download spaCy model '{self.spacy_model}', falling back to regex extraction")
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
        Extract entities from text content using spaCy NER and enhanced patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted entities with type, name, and confidence
        """
        logger.info(f"Starting entity extraction on text of length {len(text)}")
        entities = []
        
        if self.use_spacy and self.nlp:
            # Use spaCy for comprehensive entity extraction
            entities.extend(self._extract_entities_spacy(text))
        else:
            # Fallback to regex-based extraction
            entities.extend(self._extract_entities_regex(text))
        
        # Always use regex for technology and file extraction (spaCy doesn't handle these well)
        technologies = self._extract_technologies(text)
        entities.extend([{
            "type": "technology", 
            "name": tech, 
            "confidence": score
        } for tech, score in technologies])
        
        files = self._extract_file_references(text)
        entities.extend([{
            "type": "file", 
            "name": file_path, 
            "confidence": score
        } for file_path, score in files])
        
        projects = self._extract_projects(text)
        entities.extend([{
            "type": "project", 
            "name": project, 
            "confidence": score
        } for project, score in projects])
        
        logger.info(f"Entity extraction complete: found {len(entities)} total entities")
        return entities
    
    def _extract_entities_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy's NER capabilities."""
        doc = self.nlp(text)
        entities = []
        
        logger.debug(f"spaCy found {len(doc.ents)} entities in text")
        
        # Map spaCy entity labels to our entity types
        entity_mapping = {
            'PERSON': 'person',
            'ORG': 'organization', 
            'GPE': 'location',  # Countries, cities, states
            'LOC': 'location',  # Non-GPE locations
            'PRODUCT': 'product',
            'EVENT': 'event',
            'WORK_OF_ART': 'work_of_art',
            'LAW': 'law',
            'LANGUAGE': 'language',
            'DATE': 'date',
            'TIME': 'time',
            'PERCENT': 'percentage',
            'MONEY': 'money',
            'QUANTITY': 'quantity',
            'ORDINAL': 'ordinal',
            'CARDINAL': 'number'
        }
        
        for ent in doc.ents:
            entity_type = entity_mapping.get(ent.label_, ent.label_.lower())
            
            # Filter out entities that are too short or likely false positives
            if len(ent.text.strip()) < 2:
                continue
                
            # Special handling for person names
            if ent.label_ == "PERSON":
                if len(ent.text.split()) <= 3 and ent.text not in self.name_false_positives:
                    confidence = 0.9
                else:
                    continue  # Skip filtered person names
            else:
                # Confidence based on entity type and length
                confidence = min(0.8 + (len(ent.text) * 0.01), 0.95)
            
            entities.append({
                "type": entity_type,
                "name": ent.text.strip(),
                "confidence": confidence,
                "spacy_label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char
            })
            
            logger.debug(f"spaCy extracted {entity_type}: {ent.text} (confidence: {confidence})")
        
        logger.info(f"spaCy extracted {len(entities)} entities")
        return entities
    
    def _extract_entities_regex(self, text: str) -> List[Dict[str, Any]]:
        """Fallback entity extraction using regex patterns."""
        entities = []
        
        # Extract person names (existing regex logic)
        people = self._extract_people_regex(text)
        entities.extend([{
            "type": "person", 
            "name": name, 
            "confidence": score
        } for name, score in people])
        
        return entities
    
    def _extract_people(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names from text using spaCy or regex."""
        if self.use_spacy and self.nlp:
            logger.info("Using spaCy for person name extraction")
            return self._extract_people_spacy(text)
        else:
            logger.info("Using regex fallback for person name extraction")
            return self._extract_people_regex(text)
    
    def _extract_people_spacy(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names using spaCy NER."""
        doc = self.nlp(text)
        people = []
        
        logger.debug(f"spaCy found {len(doc.ents)} entities in text")
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip()
                if len(name.split()) <= 3 and name not in self.name_false_positives:
                    # spaCy confidence is typically high for NER
                    confidence = 0.9
                    people.append((name, confidence))
                    logger.debug(f"spaCy extracted person: {name} (confidence: {confidence})")
                else:
                    logger.debug(f"spaCy found person entity but filtered out: {name}")
        
        logger.info(f"spaCy extracted {len(people)} valid person names")
        return people
    
    def _extract_people_regex(self, text: str) -> List[Tuple[str, float]]:
        """Extract person names using regex patterns."""
        # Pattern for capitalized names (2-3 words max)
        name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b'
        potential_names = re.findall(name_pattern, text)
        
        logger.debug(f"Regex found {len(set(potential_names))} potential name matches")
        
        validated_names = []
        for name in set(potential_names):
            if (name not in self.name_false_positives and 
                len(name.split()) <= 3 and 
                len(name) >= 2):
                # Simple confidence scoring
                confidence = 0.8 if len(name.split()) >= 2 else 0.6
                validated_names.append((name, confidence))
                logger.debug(f"Regex extracted person: {name} (confidence: {confidence})")
            else:
                logger.debug(f"Regex found potential name but filtered out: {name}")
        
        logger.info(f"Regex extracted {len(validated_names)} valid person names")
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
        """Extract key topics and themes from content using spaCy NLP."""
        if self.use_spacy and self.nlp:
            return self._extract_topics_spacy(text)
        else:
            return self._extract_topics_regex(text)
    
    def _extract_topics_spacy(self, text: str) -> List[str]:
        """Extract topics using spaCy's NLP capabilities."""
        doc = self.nlp(text)
        topics = []
        
        # Extract noun phrases (important topics)
        for chunk in doc.noun_chunks:
            # Filter out very short or very long phrases
            if 2 <= len(chunk.text.split()) <= 4:
                topic = chunk.text.lower().strip()
                # Filter out common stop words and pronouns
                if not any(word in topic for word in ['this', 'that', 'these', 'those', 'it', 'they']):
                    topics.append(topic)
        
        # Extract important nouns and proper nouns
        important_nouns = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN'] and 
                not token.is_stop and 
                len(token.text) > 2 and
                token.text.lower() not in ['thing', 'way', 'time', 'day', 'work']):
                important_nouns.append(token.text.lower())
        
        topics.extend(important_nouns[:10])  # Limit to top 10 nouns
        
        # Extract technical terms (compound nouns)
        technical_terms = []
        for token in doc:
            if (token.pos_ == 'NOUN' and 
                token.text.isupper() or  # Acronyms
                '-' in token.text or      # Hyphenated terms
                token.text.lower() in self._get_technical_vocabulary()):
                technical_terms.append(token.text.lower())
        
        topics.extend(technical_terms)
        
        # Add regex-based technical topics as well
        regex_topics = self._extract_topics_regex(text)
        topics.extend(regex_topics)
        
        # Remove duplicates and sort by frequency
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Return topics sorted by frequency, limited to top 15
        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, count in sorted_topics[:15]]
    
    def _get_technical_vocabulary(self) -> set:
        """Get technical vocabulary relevant to software development."""
        return {
            'api', 'database', 'frontend', 'backend', 'authentication', 'authorization',
            'deployment', 'testing', 'debugging', 'optimization', 'refactoring',
            'architecture', 'framework', 'library', 'dependency', 'configuration',
            'monitoring', 'logging', 'performance', 'scalability', 'security',
            'integration', 'migration', 'versioning', 'documentation', 'deployment',
            'ci', 'cd', 'pipeline', 'automation', 'containerization', 'microservices'
        }
    
    def _extract_topics_regex(self, text: str) -> List[str]:
        """Fallback topic extraction using regex patterns."""
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
        """Extract action items and decisions from content using spaCy dependency parsing."""
        if self.use_spacy and self.nlp:
            return self._extract_action_items_spacy(content)
        else:
            return self._extract_action_items_regex(content)
    
    def _extract_action_items_spacy(self, content: str) -> List[str]:
        """Extract action items using spaCy dependency parsing."""
        doc = self.nlp(content)
        action_items = []
        
        # Action verbs that indicate tasks or decisions
        action_verbs = {
            'need', 'should', 'must', 'will', 'going', 'plan', 'decide', 'agree',
            'implement', 'fix', 'update', 'create', 'add', 'remove', 'change',
            'review', 'test', 'deploy', 'configure', 'install', 'upgrade',
            'investigate', 'research', 'analyze', 'optimize', 'refactor'
        }
        
        # Modal verbs that indicate obligations
        modal_verbs = {'need', 'should', 'must', 'will', 'going', 'plan'}
        
        for sent in doc.sents:
            # Look for action verbs in the sentence
            action_verbs_in_sent = []
            
            for token in sent:
                # Check for action verbs
                if (token.pos_ == "VERB" and 
                    token.lemma_.lower() in action_verbs and
                    not token.is_stop):
                    action_verbs_in_sent.append(token)
                
                # Check for modal verbs followed by action verbs
                elif (token.pos_ == "VERB" and 
                      token.lemma_.lower() in modal_verbs):
                    # Look for the next verb that's the actual action
                    for child in token.children:
                        if child.pos_ == "VERB" and not child.is_stop:
                            action_verbs_in_sent.append(child)
            
            # If we found action verbs, extract the action item
            if action_verbs_in_sent:
                # Get the full action phrase
                action_phrase = self._extract_action_phrase(sent, action_verbs_in_sent)
                if action_phrase and len(action_phrase.strip()) > 10:
                    action_items.append(action_phrase.strip())
        
        # Also look for explicit action item markers
        explicit_patterns = [
            r'(?:action item|todo|task):\s*([^.!?]+)',
            r'(?:TODO|FIXME|HACK):\s*([^.!?]+)',
            r'(?:next steps?|follow up):\s*([^.!?]+)'
        ]
        
        for pattern in explicit_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            action_items.extend([match.strip() for match in matches if match.strip()])
        
        return list(set(action_items))
    
    def _extract_action_phrase(self, sent, action_verbs) -> str:
        """Extract the complete action phrase from a sentence."""
        if not action_verbs:
            return ""
        
        # Start with the first action verb
        start_token = action_verbs[0]
        
        # Find the end of the action phrase (usually at a punctuation or conjunction)
        end_token = start_token
        for token in sent[start_token.i:]:
            if token.dep_ in ['punct', 'cc'] or token.text in [',', ';', 'but', 'and', 'or']:
                break
            end_token = token
        
        # Extract the phrase
        action_phrase = sent[start_token.i:end_token.i + 1].text.strip()
        
        # Clean up the phrase
        action_phrase = re.sub(r'^(?:I|we|you|they)\s+', '', action_phrase)  # Remove subject pronouns
        action_phrase = re.sub(r'\s+', ' ', action_phrase)  # Normalize whitespace
        
        return action_phrase
    
    def _extract_action_items_regex(self, content: str) -> List[str]:
        """Fallback action item extraction using regex patterns."""
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
        """Split text into sentences using spaCy's sentence segmentation."""
        if self.use_spacy and self.nlp:
            return self._split_sentences_spacy(text)
        else:
            return self._split_sentences_regex(text)
    
    def _split_sentences_spacy(self, text: str) -> List[str]:
        """Split text into sentences using spaCy's sentence segmentation."""
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        return [sent for sent in sentences if sent and len(sent.strip()) > 10]
    
    def _split_sentences_regex(self, text: str) -> List[str]:
        """Fallback sentence splitting using regex patterns."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-1 hash of content for caching."""
        return hashlib.sha1(content.encode('utf-8')).hexdigest()
    
    def _download_spacy_model(self) -> bool:
        """Download spaCy model using uv."""
        try:
            logger.info(f"Downloading spaCy model '{self.spacy_model}'")
            spacy.cli.download(self.spacy_model)
            
            logger.info(f"spaCy model '{self.spacy_model}' download completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download spaCy model '{self.spacy_model}': {e}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("uv not found in PATH, cannot download spaCy model")
            return False

    def extract_sentiment(self, text: str) -> Dict[str, Any]:
        """Extract sentiment and emotional tone from text."""
        if not self.use_spacy or not self.nlp:
            return {"sentiment": "neutral", "confidence": 0.5, "positive_score": 0.5, "negative_score": 0.5}
        
        doc = self.nlp(text)
        
        # Simple sentiment analysis based on positive/negative words
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'perfect', 'successful',
            'working', 'fixed', 'resolved', 'completed', 'finished', 'done', 'solved',
            'improved', 'enhanced', 'optimized', 'better', 'faster', 'efficient'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'broken', 'failed', 'error', 'bug', 'issue',
            'problem', 'difficult', 'hard', 'complex', 'slow', 'inefficient', 'wrong',
            'crash', 'exception', 'timeout', 'deadlock', 'memory leak'
        }
        
        positive_count = sum(1 for token in doc if token.text.lower() in positive_words)
        negative_count = sum(1 for token in doc if token.text.lower() in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            return {"sentiment": "neutral", "confidence": 0.5, "positive_score": 0.5, "negative_score": 0.5}
        
        positive_score = positive_count / total_sentiment_words
        negative_score = negative_count / total_sentiment_words
        
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = positive_score
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = negative_score
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_score": positive_score,
            "negative_score": negative_score,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases using spaCy's noun chunks and dependency parsing."""
        if not self.use_spacy or not self.nlp:
            return []
        
        doc = self.nlp(text)
        key_phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if 2 <= len(chunk.text.split()) <= 5:  # Reasonable length phrases
                phrase = chunk.text.strip()
                if len(phrase) > 5:  # Filter out very short phrases
                    key_phrases.append(phrase)
        
        # Extract verb phrases (actions)
        for token in doc:
            if token.pos_ == "VERB" and not token.is_stop:
                # Get the verb and its direct object
                verb_phrase = token.text
                for child in token.children:
                    if child.dep_ in ['dobj', 'pobj']:  # Direct object or prepositional object
                        verb_phrase += f" {child.text}"
                        break
                
                if len(verb_phrase.split()) <= 4:  # Keep phrases reasonable length
                    key_phrases.append(verb_phrase)
        
        # Remove duplicates and limit results
        unique_phrases = list(set(key_phrases))
        return unique_phrases[:max_phrases]
    
    def extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships between entities using spaCy's dependency parsing."""
        if not self.use_spacy or not self.nlp:
            return []
        
        doc = self.nlp(text)
        relationships = []
        
        # Look for subject-verb-object relationships
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ == "ROOT":
                subject = None
                obj = None
                
                # Find subject
                for child in token.children:
                    if child.dep_ in ['nsubj', 'nsubjpass']:
                        subject = child.text
                        break
                
                # Find object
                for child in token.children:
                    if child.dep_ in ['dobj', 'pobj']:
                        obj = child.text
                        break
                
                if subject and obj:
                    relationships.append({
                        "subject": subject,
                        "verb": token.text,
                        "object": obj,
                        "confidence": 0.8
                    })
        
        return relationships
    
    def extract_technical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract technical entities specific to software development."""
        if not self.use_spacy or not self.nlp:
            return []
        
        doc = self.nlp(text)
        technical_entities = []
        
        # Look for technical patterns
        for token in doc:
            # Acronyms (all caps)
            if token.text.isupper() and len(token.text) >= 2:
                technical_entities.append({
                    "type": "acronym",
                    "name": token.text,
                    "confidence": 0.9
                })
            
            # File extensions
            if token.text.startswith('.') and len(token.text) <= 5:
                technical_entities.append({
                    "type": "file_extension",
                    "name": token.text,
                    "confidence": 0.8
                })
            
            # Version numbers
            if re.match(r'v?\d+\.\d+(\.\d+)?', token.text):
                technical_entities.append({
                    "type": "version",
                    "name": token.text,
                    "confidence": 0.9
                })
        
        # Look for compound technical terms
        for i, token in enumerate(doc):
            if i < len(doc) - 1:
                next_token = doc[i + 1]
                compound = f"{token.text} {next_token.text}"
                
                # Common technical compounds
                technical_compounds = {
                    'api key', 'web service', 'data base', 'user interface',
                    'load balancer', 'cache memory', 'error handling',
                    'code review', 'unit test', 'integration test'
                }
                
                if compound.lower() in technical_compounds:
                    technical_entities.append({
                        "type": "technical_term",
                        "name": compound,
                        "confidence": 0.8
                    })
        
        return technical_entities


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