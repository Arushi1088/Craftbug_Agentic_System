// Test script to verify scenario loading
const BASE_URL = 'http://127.0.0.1:8000';

async function testScenarioLoading() {
    console.log('🧪 Testing Scenario Loading...');
    
    try {
        // Test 1: Get all scenarios
        console.log('\n📊 Test 1: Getting all scenarios...');
        const response = await fetch(`${BASE_URL}/api/scenarios`);
        const data = await response.json();
        console.log(`✅ Total scenarios: ${data.scenarios.length}`);
        
        // Test 2: Filter Word scenarios
        console.log('\n📄 Test 2: Filtering Word scenarios...');
        const wordScenarios = data.scenarios.filter(s => s.app_type === 'word');
        console.log(`✅ Word scenarios: ${wordScenarios.length}`);
        wordScenarios.forEach(s => console.log(`   - ${s.name} (${s.app_type})`));
        
        // Test 3: Filter Excel scenarios
        console.log('\n📊 Test 3: Filtering Excel scenarios...');
        const excelScenarios = data.scenarios.filter(s => s.app_type === 'excel');
        console.log(`✅ Excel scenarios: ${excelScenarios.length}`);
        excelScenarios.forEach(s => console.log(`   - ${s.name} (${s.app_type})`));
        
        // Test 4: Filter PowerPoint scenarios
        console.log('\n📽️ Test 4: Filtering PowerPoint scenarios...');
        const powerpointScenarios = data.scenarios.filter(s => s.app_type === 'powerpoint');
        console.log(`✅ PowerPoint scenarios: ${powerpointScenarios.length}`);
        powerpointScenarios.forEach(s => console.log(`   - ${s.name} (${s.app_type})`));
        
        console.log('\n🎯 Test completed successfully!');
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

// Run the test
testScenarioLoading();
