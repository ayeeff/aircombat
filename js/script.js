const countries = [
    {code: 'us', name: 'United States', rank: 1, fps: 5751, li: 95.9, flag: 'https://flagcdn.com/w80/us.png', 
     aircraftMix: 'F-22 / F-35 / F-15EX / F/A-18E/F', primaryBVR: 'AIM-120D / AIM-260',
     a: 95, b: 98, c: 96, d: 98, e: 96, f: 95, g: 90},
    {code: 'ru', name: 'Russia', rank: 2, fps: 5678, li: 94.6, flag: 'https://flagcdn.com/w80/ru.png',
     aircraftMix: 'Su-57 / Su-35S / Su-30SM / MiG-31BM', primaryBVR: 'R-37M / R-77-1',
     a: 92, b: 85, c: 98, d: 88, e: 90, f: 92, g: 95},
    {code: 'cn', name: 'China', rank: 3, fps: 5660, li: 94.3, flag: 'https://flagcdn.com/w80/cn.png',
     aircraftMix: 'J-20 / J-16 / J-10C / Su-35SK', primaryBVR: 'PL-15 / PL-17',
     a: 90, b: 88, c: 95, d: 92, e: 88, f: 94, g: 98},
    {code: 'il', name: 'Israel', rank: 4, fps: 5604, li: 93.4, flag: 'https://flagcdn.com/w80/il.png',
     aircraftMix: 'F-35I / F-15I / F-16I', primaryBVR: 'Derby / AIM-120C',
     a: 94, b: 90, c: 92, d: 95, e: 96, f: 88, g: 85},
    {code: 'gb', name: 'United Kingdom', rank: 5, fps: 5436, li: 90.6, flag: 'https://flagcdn.com/w80/gb.png',
     aircraftMix: 'F-35B / Typhoon FGR4', primaryBVR: 'Meteor / AIM-120C',
     a: 88, b: 92, c: 94, d: 90, e: 88, f: 85, g: 80},
    {code: 'au', name: 'Australia', rank: 6, fps: 5386, li: 89.8, flag: 'https://flagcdn.com/w80/au.png',
     aircraftMix: 'F-35A / F/A-18F', primaryBVR: 'AIM-120D / AIM-260',
     a: 90, b: 88, c: 92, d: 88, e: 85, f: 82, g: 78},
    {code: 'jp', name: 'Japan', rank: 7, fps: 5370, li: 89.5, flag: 'https://flagcdn.com/w80/jp.png',
     aircraftMix: 'F-35A/B / F-15J / F-2', primaryBVR: 'AAM-4B / AIM-120C',
     a: 88, b: 86, c: 90, d: 90, e: 88, f: 84, g: 76},
    {code: 'kr', name: 'South Korea', rank: 8, fps: 5322, li: 88.7, flag: 'https://flagcdn.com/w80/kr.png',
     aircraftMix: 'F-35A / F-15K / KF-21', primaryBVR: 'AIM-120C / Meteor',
     a: 86, b: 84, c: 90, d: 88, e: 86, f: 85, g: 82},
    {code: 'se', name: 'Sweden', rank: 9, fps: 5319, li: 88.7, flag: 'https://flagcdn.com/w80/se.png',
     aircraftMix: 'Gripen E/C', primaryBVR: 'Meteor / AIM-120C',
     a: 84, b: 88, c: 94, d: 86, e: 90, f: 82, g: 74},
    {code: 'it', name: 'Italy', rank: 10, fps: 5316, li: 88.6, flag: 'https://flagcdn.com/w80/it.png',
     aircraftMix: 'F-35A/B / Typhoon', primaryBVR: 'Meteor / AIM-120C',
     a: 86, b: 88, c: 92, d: 88, e: 86, f: 80, g: 75},
    {code: 'fr', name: 'France', rank: 11, fps: 5311, li: 88.5, flag: 'https://flagcdn.com/w80/fr.png',
     aircraftMix: 'Rafale F4', primaryBVR: 'Meteor / MICA-NG',
     a: 85, b: 86, c: 93, d: 90, e: 88, f: 84, g: 76},
    {code: 'ca', name: 'Canada', rank: 12, fps: 5204, li: 86.7, flag: 'https://flagcdn.com/w80/ca.png',
     aircraftMix: 'F/A-18E/F / F-35A (future)', primaryBVR: 'AIM-120C',
     a: 82, b: 80, c: 88, d: 86, e: 84, f: 78, g: 70},
    {code: 'de', name: 'Germany', rank: 13, fps: 4901, li: 81.7, flag: 'https://flagcdn.com/w80/de.png',
     aircraftMix: 'Typhoon / F-35A (future)', primaryBVR: 'Meteor / AIM-120C',
     a: 84, b: 82, c: 90, d: 82, e: 80, f: 74, g: 68},
    {code: 'tr', name: 'Turkey', rank: 14, fps: 4770, li: 79.5, flag: 'https://flagcdn.com/w80/tr.png',
     aircraftMix: 'F-16C/D Block 50+', primaryBVR: 'AIM-120C',
     a: 78, b: 75, c: 85, d: 80, e: 82, f: 80, g: 85},
    {code: 'pk', name: 'Pakistan', rank: 15, fps: 4743, li: 79.1, flag: 'https://flagcdn.com/w80/pk.png',
     aircraftMix: 'JF-17 Block III / F-16C/D', primaryBVR: 'PL-15 / AIM-120C',
     a: 76, b: 72, c: 88, d: 78, e: 78, f: 82, g: 80},
    {code: 'th', name: 'Thailand', rank: 16, fps: 4707, li: 78.5, flag: 'https://flagcdn.com/w80/th.png',
     aircraftMix: 'Gripen C/D / F-16A/B MLU', primaryBVR: 'AIM-120C / Derby',
     a: 75, b: 74, c: 84, d: 76, e: 78, f: 76, g: 72},
    {code: 'es', name: 'Spain', rank: 17, fps: 4698, li: 78.3, flag: 'https://flagcdn.com/w80/es.png',
     aircraftMix: 'Typhoon / F/A-18C/D+', primaryBVR: 'Meteor / AIM-120C',
     a: 82, b: 80, c: 88, d: 78, e: 76, f: 72, g: 66},
    {code: 'ir', name: 'Iran', rank: 18, fps: 4617, li: 76.9, flag: 'https://flagcdn.com/w80/ir.png',
     aircraftMix: 'F-14A / MiG-29 / Su-35S (future)', primaryBVR: 'Fakour-90 / R-77',
     a: 70, b: 68, c: 82, d: 72, e: 74, f: 78, g: 88},
    {code: 'in', name: 'India', rank: 19, fps: 4617, li: 76.9, flag: 'https://flagcdn.com/w80/in.png',
     aircraftMix: 'Rafale / Su-30MKI / MiG-29UPG', primaryBVR: 'Meteor / R-77 / Astra',
     a: 82, b: 76, c: 85, d: 75, e: 76, f: 70, g: 74},
    {code: 'sa', name: 'Saudi Arabia', rank: 20, fps: 4548, li: 75.8, flag: 'https://flagcdn.com/w80/sa.png',
     aircraftMix: 'Typhoon / F-15SA', primaryBVR: 'Meteor / AIM-120C',
     a: 80, b: 78, c: 86, d: 76, e: 74, f: 68, g: 70}
];

const csvMap = {
    'us': 'us.csv', 'ru': 'rus.csv', 'cn': 'chn.csv', 'il': 'isr.csv',
    'gb': 'uk.csv', 'au': 'aus.csv', 'jp': 'jpn.csv', 'kr': 'kor.csv',
    'se': 'swe.csv', 'it': 'ita.csv', 'fr': 'fra.csv', 'ca': 'can.csv',
    'de': 'de.csv', 'tr': 'tuk.csv', 'pk': 'pk.csv', 'th': 'thai.csv',
    'es': 'spa.csv', 'ir': 'iran.csv', 'in': 'in.csv', 'sa': 'sau.csv'
};

const subsystems = [
    {key: 'a', label: 'A. Sensor reach', weight: '22.5%', color: '#3b82f6'},
    {key: 'b', label: 'B. Signature control', weight: '15%', color: '#a78bfa'},
    {key: 'c', label: 'C. Missile reach', weight: '22.5%', color: '#ef4444'},
    {key: 'd', label: 'D. Kill-chain network', weight: '15%', color: '#22c55e'},
    {key: 'e', label: 'E. ECM / self-protection', weight: '10%', color: '#f97316'},
    {key: 'f', label: 'F. Sustained sortie rate', weight: '5%', color: '#06b6d4'},
    {key: 'g', label: 'G. UCAV/drone/CCA', weight: '10%', color: '#ec4899'}
];

let fleetData = {};
let activeTab = 'us';

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
    for (const country of countries) {
        try {
            fleetData[country.code] = await loadCSV(country.code);
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

function switchTab(countryCode) {
    activeTab = countryCode;
    
    // Update button states
    document.querySelectorAll('.tab-button').forEach((btn, idx) => {
        btn.classList.toggle('active', countries[idx].code === countryCode);
    });
    
    // Render content
    renderTabContent(countryCode);
    renderStatsPanel(countryCode);
}

function renderStatsPanel(countryCode) {
    const country = countries.find(c => c.code === countryCode);
    const statsPanel = document.getElementById('statsPanel');
    
    statsPanel.innerHTML = `
        <h3 class="text-2xl font-bold text-white mb-4 orbitron text-center">Combat Index</h3>
        
        <div class="li-score">${country.li}</div>
        
        <div class="stat-item">
            <div class="stat-label">Aircraft Mix</div>
            <div class="stat-value text-sm">${country.aircraftMix}</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Primary BVR Missile</div>
            <div class="stat-value text-sm">${country.primaryBVR}</div>
        </div>
        
        <div class="stat-item">
            <div class="stat-label">Fleet Power Score (FPS)</div>
            <div class="stat-value">${country.fps}</div>
        </div>
        
        <h4 class="text-xl font-bold text-white mt-6 mb-4 orbitron">⚡ Sub-Systems</h4>
        
        ${subsystems.map(sub => `
            <div class="subsystem-row">
                <div class="subsystem-label">
                    <span class="text-slate-300 text-sm">${sub.label}</span>
                    <span class="text-xs text-slate-500">${sub.weight}</span>
                </div>
                <div class="subsystem-score" style="color: ${sub.color}">${country[sub.key]}</div>
                <div class="score-bar">
                    <div class="score-fill" style="width: ${country[sub.key]}%; background: ${sub.color}"></div>
                </div>
            </div>
        `).join('')}
    `;
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
                    <h2 class="text-3xl font-bold orbitron">${country.name}</h2>
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
    renderStatsPanel('us');
}

init();
