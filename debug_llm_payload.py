#!/usr/bin/env python3
"""
Debug LLM Payload - See exactly what's being sent to the LLM
"""

import asyncio
from final_craft_bug_analyzer import FinalCraftBugAnalyzer

async def debug_llm_payload():
    """Debug what payload is being sent to the LLM"""
    
    # Sample test data
    test_steps = [
        {
            'step_name': 'Navigate to Excel',
            'description': 'User navigates to Excel web app',
            'screenshot_path': 'screenshots/excel_web/excel_initial_state_1756061972.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Dismiss Copilot Dialog',
            'description': 'User dismisses the Copilot dialog',
            'screenshot_path': 'screenshots/excel_web/excel_copilot_dialog_1756061967.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        },
        {
            'step_name': 'Save Workbook',
            'description': 'User saves the workbook',
            'screenshot_path': 'screenshots/excel_web/excel_final_state_1755521895.png',
            'scenario_description': 'Excel Document Creation with Copilot',
            'persona_type': 'Power User'
        }
    ]
    
    # Initialize analyzer
    analyzer = FinalCraftBugAnalyzer()
    
    # Prepare context and images
    context = analyzer._prepare_context(test_steps)
    image_files = await analyzer._prepare_images(test_steps)
    
    print(f"📊 Context: {context}")
    print(f"📸 Images: {len(image_files)} files")
    
    # Build the messages payload (same as the analyzer does)
    prompt = analyzer.final_prompt.format(
        scenario_description=context['scenario_description'],
        persona_type=context['persona_type'],
        step_description_1="Step 1: User navigates to Excel web app",
        screenshot_1="[attached]",
        step_description_2="Step 2: User dismisses the Copilot dialog", 
        screenshot_2="[attached]",
        step_description_3="Step 3: User saves the workbook",
        screenshot_3="[attached]"
    )
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ]
    
    # Add images to the message
    for i, (image_path, image_data) in enumerate(image_files):
        import base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        messages[0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })
    
    print(f"\n🔍 MESSAGES PAYLOAD STRUCTURE:")
    print(f"   Model: {analyzer.llm_model}")
    print(f"   Max Tokens: {analyzer.llm_max_tokens}")
    print(f"   Temperature: {analyzer.llm_temperature}")
    print(f"   Content Items: {len(messages[0]['content'])}")
    
    for i, item in enumerate(messages[0]['content']):
        if item['type'] == 'text':
            print(f"   Item {i}: TEXT ({len(item['text'])} chars)")
            print(f"      Preview: {item['text'][:200]}...")
        elif item['type'] == 'image_url':
            print(f"   Item {i}: IMAGE_URL")
            print(f"      URL: {item['image_url']['url'][:100]}...")
    
    print(f"\n📊 PAYLOAD SUMMARY:")
    print(f"   Text content: {len([x for x in messages[0]['content'] if x['type'] == 'text'])} items")
    print(f"   Image content: {len([x for x in messages[0]['content'] if x['type'] == 'image_url'])} items")
    print(f"   Total content: {len(messages[0]['content'])} items")
    
    # Check if images are actually being sent
    image_count = len([x for x in messages[0]['content'] if x['type'] == 'image_url'])
    if image_count == 0:
        print("\n❌ PROBLEM: No images are being sent to the LLM!")
        print("   This explains why we're getting generic bugs.")
    else:
        print(f"\n✅ Images are being sent: {image_count} images")
        print("   The issue might be with the prompt or model response.")

if __name__ == "__main__":
    asyncio.run(debug_llm_payload())

