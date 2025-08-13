// Debug script to test scenario filtering
const BASE_URL = 'http://localhost:8000';

async function debugScenarioFiltering() {
    console.log('🔍 Debugging Scenario Filtering...');
    
    try {
        // Test 1: Get all scenarios
        console.log('\n📊 Test 1: Getting all scenarios...');
        const response = await fetch(`${BASE_URL}/api/scenarios`);
        const data = await response.json();
        console.log(`✅ Total scenarios: ${data.scenarios.length}`);
        
        // Test 2: Test frontend filtering logic
        console.log('\n🔧 Test 2: Testing frontend filtering logic...');
        const allScenarios = data.scenarios || [];
        
        // Test each app type
        ['word', 'excel', 'powerpoint'].forEach(appType => {
            const filteredScenarios = allScenarios.filter(scenario => scenario.app_type === appType);
            console.log(`📱 ${appType.toUpperCase()} scenarios: ${filteredScenarios.length}`);
            
            if (filteredScenarios.length > 0) {
                console.log(`   Available scenarios:`);
                filteredScenarios.forEach(s => {
                    console.log(`   - ${s.name} (ID: ${s.id}, Type: ${s.app_type})`);
                });
            } else {
                console.log(`   ❌ No scenarios found for ${appType}`);
            }
        });
        
        // Test 3: Check for any scenarios with wrong app_type
        console.log('\n🔍 Test 3: Checking for mislabeled scenarios...');
        const wordScenarios = allScenarios.filter(s => s.name.toLowerCase().includes('word'));
        const excelScenarios = allScenarios.filter(s => s.name.toLowerCase().includes('excel'));
        const powerpointScenarios = allScenarios.filter(s => s.name.toLowerCase().includes('powerpoint') || s.name.toLowerCase().includes('slide'));
        
        console.log(`📄 Scenarios with 'word' in name: ${wordScenarios.length}`);
        wordScenarios.forEach(s => {
            console.log(`   - ${s.name} (app_type: ${s.app_type})`);
        });
        
        console.log(`📊 Scenarios with 'excel' in name: ${excelScenarios.length}`);
        excelScenarios.forEach(s => {
            console.log(`   - ${s.name} (app_type: ${s.app_type})`);
        });
        
        console.log(`📽️ Scenarios with 'powerpoint'/'slide' in name: ${powerpointScenarios.length}`);
        powerpointScenarios.forEach(s => {
            console.log(`   - ${s.name} (app_type: ${s.app_type})`);
        });
        
        console.log('\n✅ Debug completed!');
        
    } catch (error) {
        console.error('❌ Debug failed:', error);
    }
}

// Run the debug
debugScenarioFiltering();
