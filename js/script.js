const countries = [
    {code: 'us', name: 'United States', rank: 1, fps: 5751, flag: 'https://flagcdn.com/w80/us.png'},
    {code: 'ru', name: 'Russia', rank: 2, fps: 5678, flag: 'https://flagcdn.com/w80/ru.png'},
    {code: 'cn', name: 'China', rank: 3, fps: 5660, flag: 'https://flagcdn.com/w80/cn.png'},
    {code: 'il', name: 'Israel', rank: 4, fps: 5604, flag: 'https://flagcdn.com/w80/il.png'},
    {code: 'gb', name: 'United Kingdom', rank: 5, fps: 5436, flag: 'https://flagcdn.com/w80/gb.png'},
    {code: 'au', name: 'Australia', rank: 6, fps: 5386, flag: 'https://flagcdn.com/w80/au.png'},
    {code: 'jp', name: 'Japan', rank: 7, fps: 5370, flag: 'https://flagcdn.com/w80/jp.png'},
    {code: 'kr', name: 'South Korea', rank: 8, fps: 5322, flag: 'https://flagcdn.com/w80/kr.png'},
    {code: 'se', name: 'Sweden', rank: 9, fps: 5319, flag: 'https://flagcdn.com/w80/se.png'},
    {code: 'it', name: 'Italy', rank: 10, fps: 5316, flag: 'https://flagcdn.com/w80/it.png'},
    {code: 'fr', name: 'France', rank: 11, fps: 5311, flag: 'https://flagcdn.com/w80/fr.png'},
    {code: 'ca', name: 'Canada', rank: 12, fps: 5204, flag: 'https://flagcdn.com/w80/ca.png'},
    {code: 'de', name: 'Germany', rank: 13, fps: 4901, flag: 'https://flagcdn.com/w80/de.png'},
    {code: 'tr', name: 'Turkey', rank: 14, fps: 4770, flag: 'https://flagcdn.com/w80/tr.png'},
    {code: 'pk', name: 'Pakistan', rank: 15, fps: 4743, flag: 'https://flagcdn.com/w80/pk.png'},
    {code: 'th', name: 'Thailand', rank: 16, fps: 4707, flag: 'https://flagcdn.com/w80/th.png'},
    {code: 'es', name: 'Spain', rank: 17, fps: 4698, flag: 'https://flagcdn.com/w80/es.png'},
    {code: 'ir', name: 'Iran', rank: 18, fps: 4617, flag: 'https://flagcdn.com/w80/ir.png'},
    {code: 'in', name: 'India', rank: 19, fps: 4617, flag: 'https://flagcdn.com/w80/in.png'},
    {code: 'sa', name: 'Saudi Arabia', rank: 20, fps: 4548, flag: 'https://flagcdn.com/w80/sa.png'}
];

const csvMap = {
    'us': 'us.csv', 'ru': 'rus.csv', 'cn': 'chn.csv', 'il': 'isr.csv',
    'gb': 'uk.csv', 'au': 'aus.csv', 'jp': 'jpn.csv', 'kr': 'kor.csv',
    'se': 'swe.csv', 'it': 'ita.csv', 'fr': 'fra.csv', 'ca': 'can.csv',
    'de': 'de.csv', 'tr': 'tuk.csv', 'pk': 'pk.csv', 'th': 'thai.csv',
    'es': 'spa.csv', 'ir': 'iran.csv', 'in': 'in.csv', 'sa': 'sau.csv'
};

let fleetData = {};
let activeTab = 'us';
let loadedTabs = new Set();

async function loadCSV(countryCode) {
    const csvFile = csvMap[countryCode];
    const url = `https://raw.githubusercontent.com/ayeeff/aircombat/main/data/${csvFile}`;
    
    return new Promise((resolve, reject) => {
        Papa.parse(url, {
            download: true,
            header: true,
            complete: (results) => resolve(results.data),
            error: (error) => reject(error)
        });
    });
}

async function loadAllData() {
    // Load US data first
    try {
        fleetData['us'] = await loadCSV('us');
        loadedTabs.add('us');
    } catch (error) {
        console.error('Error loading United States:', error);
        fleetData['us'] = [];
    }
    
    // Load remaining countries in background
    loadRemainingCountries();
}

async function loadRemainingCountries() {
    for (const country of countries) {
        if (country.code === 'us') continue;
        
        try {
            fleetData[country.code] = await loadCSV(country.code);
            loadedTabs.add(country.code);
        } catch (error) {
            console.error(`Error loading ${country.name}:`, error);
            fleetData[country.code] = [];
        }
    }
}

function createTabs() {
    const tabButtons = document.getElementById('tabButtons');
    
    countries.forEach(country => {
        const button = document.createElement('button');
        button.className = `tab-button px-4 py-3 rounded-lg font-semibold flex items-center gap-2 ${country.code === 'us' ? 'active' : ''}`;
        button.innerHTML = `
            <img src="${country.flag}" alt="${country.name}" class="w-6 h-4 flag-badge rounded">
            <span class="text-sm">#${country.rank} ${country.name}</span>
            <span class="text-xs text-slate-400">(${country.fps})</span>
        `;
        button.onclick = () => switchTab(country.code);
        tabButtons.appendChild(button);
    });
}

async function switchTab(countryCode) {
    activeTab = countryCode;
    
    // Update button states
    document.querySelectorAll('.tab-button').forEach((btn, idx) => {
        btn.classList.toggle('active', countries[idx].code === countryCode);
    });
    
    // Check if data is loaded, if not show loading state
    if (!loadedTabs.has(countryCode)) {
        document.getElementById('tabContent').innerHTML = `
            <div class="text-center py-20">
                <div class="loading-spinner w-16 h-16 rounded-full mx-auto mb-4"></div>
                <p class="text-slate-400">Loading data...</p>
            </div>
        `;
        
        // Wait for data to load
        while (!loadedTabs.has(countryCode)) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }
    
    // Render content
    renderTabContent(countryCode);
}

function renderTabContent(countryCode) {
    const country = countries.find(c => c.code === countryCode);
    const aircraft = fleetData[countryCode] || [];
    const tabContent = document.getElementById('tabContent');
    
    tabContent.innerHTML = `
        <div class="aircraft-card rounded-2xl p-6 mb-6">
            <div class="flex items-center gap-4 mb-4">
                <img src="${country.flag}" alt="${country.name}" class="w-16 h-10 flag-badge rounded-lg">
                <div>
                    <h2 class="text-3xl font-bold text-white orbitron">${country.name}</h2>
                    <p class="text-slate-400">Rank #${country.rank} • FPS: ${country.fps}</p>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 gap-6">
            ${aircraft.map((ac, idx) => {
                if (!ac.Aircraft) return '';
                return `
                    <div class="aircraft-card rounded-2xl overflow-hidden">
                        <div class="grid md:grid-cols-3 gap-6 p-6">
                            <div class="md:col-span-1">
                                <img src="${ac.Photo || 'https://via.placeholder.com/400x300?text=No+Image'}" 
                                     alt="${ac.Aircraft}" 
                                     class="w-full h-64 object-cover rounded-lg"
                                     loading="lazy"
                                     onerror="this.src='https://via.placeholder.com/400x300?text=No+Image'">
                                <div class="mt-4 space-y-2">
                                    <div class="flex items-center gap-2">
                                        <span class="text-blue-400 font-semibold">Type:</span>
                                        <span class="text-slate-300">${ac.Type}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-purple-400 font-semibold">Origin:</span>
                                        <span class="text-slate-300">${ac.Origin}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-green-400 font-semibold">Version:</span>
                                        <span class="text-slate-300">${ac.Versions}</span>
                                    </div>
                                    <div class="flex items-center gap-2">
                                        <span class="text-yellow-400 font-semibold">In Service:</span>
                                        <span class="text-white font-bold text-lg">${ac['In Service']}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="md:col-span-2">
                                <h3 class="text-2xl font-bold text-white mb-3 orbitron">${ac.Aircraft}</h3>
                                <p class="text-slate-300 leading-relaxed">${ac.Notes}</p>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

// Initialize
async function init() {
    await loadAllData();
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('tabsContainer').classList.remove('hidden');
    createTabs();
    renderTabContent('us');
}

init();
