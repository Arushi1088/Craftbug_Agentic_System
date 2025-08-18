"""
Test script for Excel Web document creation scenario
"""

import asyncio
import sys
from excel_web_navigator import get_excel_web_navigator
from excel_scenarios import get_excel_scenario_executor


async def test_document_creation_scenario():
    """Test the Excel Web document creation scenario"""
    navigator = await get_excel_web_navigator()
    executor = await get_excel_scenario_executor(navigator)
    
    try:
        print("🧪 Testing Excel Web Document Creation Scenario...")
        
        # Initialize navigator
        if not await navigator.initialize():
            print("❌ Failed to initialize navigator")
            return False
        
        # Execute the document creation scenario
        result = await executor.execute_document_creation_scenario()
        
        # Print detailed results
        print("\n" + "=" * 60)
        print("📊 FINAL RESULTS")
        print("=" * 60)
        print(f"Scenario: {result.scenario_name}")
        print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
        print(f"Steps Completed: {result.steps_completed}/{result.total_steps}")
        print(f"Execution Time: {result.execution_time:.2f} seconds")
        print(f"Screenshots Taken: {len(result.screenshots)}")
        
        if result.screenshots:
            print("\n📸 Screenshots:")
            for screenshot in result.screenshots:
                print(f"   - {screenshot}")
        
        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"   - {error}")
        
        # Performance metrics
        if result.performance_metrics:
            print(f"\n⏱️  Performance Metrics:")
            total_step_time = sum(result.performance_metrics.values())
            avg_step_time = total_step_time / len(result.performance_metrics)
            print(f"   Average Step Time: {avg_step_time:.2f}s")
            print(f"   Total Step Time: {total_step_time:.2f}s")
            print(f"   Overhead Time: {result.execution_time - total_step_time:.2f}s")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Cleanup
        await navigator.close()


async def main():
    """Main test function"""
    print("🚀 Starting Excel Web Document Creation Scenario Test")
    print("=" * 60)
    
    success = await test_document_creation_scenario()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Document creation scenario test passed!")
        print("✅ Excel Web automation is working correctly!")
        sys.exit(0)
    else:
        print("💥 Document creation scenario test failed!")
        print("❌ Excel Web automation needs debugging")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
