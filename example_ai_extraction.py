"""
Example: AI Entity Extraction & Enhancement Demo
Phase 2.2: Demonstrates AI-powered content analysis and entity extraction.
"""

import tempfile
from pathlib import Path
from core import UnifiedMemoryStore
from models import MemoryContext, MemoryEntity


def demo_ai_extraction():
    """Demonstrate AI extraction functionality with realistic content."""
    
    # Create temporary database
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "ai_demo.db"
        
        print("🚀 Initializing Unified Memory Store with AI Extraction...")
        memory_store = UnifiedMemoryStore(
            db_path=db_path,
            enable_vector_search=False,  # Disable for demo
            enable_ai_extraction=True
        )
        
        print("\n📝 Example 1: Handoff Conversation")
        print("=" * 50)
        
        handoff_content = """
        Handoff from John Smith to Sarah Johnson:
        
        We had a productive debugging session today. The main issue was with the React authentication system.
        The problem seems to be in the main.py file where the JWT token validation is failing.
        
        Key findings:
        - The PostgreSQL database connection is working fine
        - The issue is specifically in the auth middleware
        - We need to check the utils/helper.js file for the token parsing logic
        
        Action items:
        - Sarah needs to review the authentication flow in src/components/Auth.js
        - We should update the API documentation to reflect the new token format
        - Next steps: Deploy the fix to staging environment
        
        Technologies discussed: React, TypeScript, PostgreSQL, JWT
        Files mentioned: main.py, utils/helper.js, src/components/Auth.js
        """
        
        handoff_context = MemoryContext(
            type="handoff",
            content=handoff_content
        )
        
        print("Original content length:", len(handoff_content))
        print("Saving context with AI enhancement...")
        
        saved_handoff = memory_store.save_context(handoff_context)
        
        print("\n✅ AI Enhancement Results:")
        print(f"  • Topics extracted: {saved_handoff.topics}")
        print(f"  • Summary generated: {saved_handoff.summary}")
        print(f"  • Action items: {saved_handoff.metadata.get('action_items', [])}")
        print(f"  • Entities created/linked: {len(saved_handoff.entity_ids)}")
        
        # Show extracted entities
        extracted_entities = saved_handoff.metadata.get('extracted_entities', [])
        print(f"  • Entities extracted: {len(extracted_entities)}")
        for entity in extracted_entities[:5]:  # Show first 5
            action = "🔗 LINKED" if entity['action'] == 'link' else "🆕 CREATED"
            print(f"    {action} {entity['type']}: {entity['name']} (confidence: {entity['confidence']:.2f})")
        
        print("\n📝 Example 2: Meeting Notes")
        print("=" * 50)
        
        meeting_content = """
        Sprint Planning Meeting - Ecommerce Project
        
        Attendees: Mike Wilson, Lisa Chen, David Rodriguez
        
        Discussion:
        - We're behind schedule on the payment integration feature
        - The Stripe API integration is working, but we need to handle webhook failures better
        - Performance issues in the product catalog page need attention
        
        Decisions made:
        - We'll use Redis for caching product data
        - David will take ownership of the payment system
        - Lisa will focus on the frontend performance optimization
        
        Technical debt:
        - The old authentication system in auth/legacy.py needs to be removed
        - Database migrations are pending for the new user schema
        
        Next sprint priorities:
        1. Complete Stripe webhook error handling
        2. Implement Redis caching layer
        3. Optimize product catalog queries
        4. Remove legacy authentication code
        """
        
        meeting_context = MemoryContext(
            type="meeting",
            content=meeting_content
        )
        
        print("Saving meeting context with AI enhancement...")
        saved_meeting = memory_store.save_context(meeting_context)
        
        print("\n✅ Meeting Enhancement Results:")
        print(f"  • Topics: {saved_meeting.topics}")
        print(f"  • Summary: {saved_meeting.summary}")
        print(f"  • Action items: {len(saved_meeting.metadata.get('action_items', []))}")
        
        print("\n📝 Example 3: Code Review Discussion")
        print("=" * 50)
        
        code_review_content = """
        Code Review: PR #123 - User Authentication Refactor
        
        Reviewer: Alex Thompson
        Author: Maria Garcia
        
        The refactor looks good overall, but I have a few concerns:
        
        Issues found:
        - The new auth.py file has some hardcoded values that should be configurable
        - Missing error handling in the login function
        - The test coverage for auth/test_login.py is insufficient
        
        Positive aspects:
        - Clean separation of concerns in the new structure
        - Good use of TypeScript for type safety
        - Proper integration with the existing PostgreSQL schema
        
        Suggestions:
        - Consider using environment variables for the JWT secret
        - Add more comprehensive error logging
        - The utils/validation.js helper could be reused here
        
        Files changed:
        - src/auth/auth.py (new)
        - src/auth/test_login.py (new)
        - src/components/Login.js (modified)
        - config/database.py (modified)
        
        Technologies: TypeScript, JWT, PostgreSQL, Jest
        """
        
        review_context = MemoryContext(
            type="code_review",
            content=code_review_content
        )
        
        print("Saving code review context with AI enhancement...")
        saved_review = memory_store.save_context(review_context)
        
        print("\n✅ Code Review Enhancement Results:")
        print(f"  • Topics: {saved_review.topics}")
        print(f"  • Summary: {saved_review.summary}")
        print(f"  • Files mentioned: {len([e for e in saved_review.metadata.get('extracted_entities', []) if e['type'] == 'file'])}")
        
        print("\n🔍 Cross-Context Search Demo")
        print("=" * 50)
        
        # Search for all contexts mentioning authentication
        auth_contexts = memory_store.search_contexts("authentication")
        print(f"Found {len(auth_contexts)} contexts mentioning authentication:")
        
        for i, ctx in enumerate(auth_contexts, 1):
            print(f"  {i}. {ctx.type}: {ctx.summary[:100]}...")
        
        # Search for all contexts mentioning React
        react_contexts = memory_store.search_contexts("React")
        print(f"\nFound {len(react_contexts)} contexts mentioning React:")
        
        for i, ctx in enumerate(react_contexts, 1):
            print(f"  {i}. {ctx.type}: {ctx.summary[:100]}...")
        
        print("\n👥 Entity Relationship Demo")
        print("=" * 50)
        
        # Show some relationships
        all_entities = memory_store.search("", limit=10)
        print(f"Total entities in system: {len(all_entities)}")
        
        for entity in all_entities[:5]:
            related = memory_store.get_related(entity['id'])
            print(f"  {entity['type']}: {entity['name']} - {len(related)} relationships")
        
        print("\n🎯 Direct AI Extraction Methods")
        print("=" * 50)
        
        test_text = "John Smith and Sarah Johnson are working on the React project using TypeScript and PostgreSQL."
        
        print(f"Test text: {test_text}")
        print(f"Entities: {memory_store.extract_entities_from_text(test_text)}")
        print(f"Topics: {memory_store.extract_topics_from_text(test_text)}")
        print(f"Summary: {memory_store.generate_summary(test_text, max_length=50)}")
        
        action_text = "We need to fix the bug. Action item: Update the database schema. Next steps: Deploy to production."
        print(f"\nAction text: {action_text}")
        print(f"Action items: {memory_store.extract_action_items(action_text)}")
        
        print("\n✅ AI Extraction Demo Complete!")
        print("The system successfully:")
        print("  • Extracted entities (people, technologies, files, projects)")
        print("  • Generated summaries for long content")
        print("  • Identified topics and themes")
        print("  • Extracted action items and decisions")
        print("  • Created relationships between content and entities")
        print("  • Enabled cross-context search and discovery")


if __name__ == "__main__":
    demo_ai_extraction() 