     const data = [
            {rank: 1, country: "United States", countryCode: "us", aircraft: "F-22A (20) + F-35A Blk-4 (25) + F-15EX (15)", missile: "AIM-120D-3 (180) / AIM-260 (230)", A: 98, B: 96, C: 92, D: 99, E: 97, F: 93, LI: 96.1, FPS: 5766},
            {rank: 2, country: "Russia", countryCode: "ru", aircraft: "Su-57 (12) + Su-35S (28) + Su-30SM2 (20)", missile: "R-77M (200) / R-37M (400)", A: 95, B: 88, C: 100, D: 96, E: 94, F: 85, LI: 94.8, FPS: 5688},
            {rank: 3, country: "China", countryCode: "cn", aircraft: "J-20A (40) + J-35A (20)", missile: "PL-15 (200) / PL-21 (300)", A: 97, B: 90, C: 94, D: 97, E: 89, F: 88, LI: 94.0, FPS: 5640},
            {rank: 4, country: "Israel", countryCode: "il", aircraft: "F-35I (39) + F-15IA (21)", missile: "AIM-120D-3 (180) + Rampage ALBM (250)", A: 96, B: 95, C: 88, D: 97, E: 97, F: 90, LI: 93.9, FPS: 5634},
            {rank: 5, country: "United Kingdom", countryCode: "gb", aircraft: "F-35B (30) + Typhoon FGR4 (30)", missile: "Meteor (150) / AIM-120D-3 (180)", A: 94, B: 92, C: 88, D: 94, E: 94, F: 87, LI: 91.8, FPS: 5508},
            {rank: 6, country: "Japan", countryCode: "jp", aircraft: "F-35A (38) + F-15J MSIP (22)", missile: "AIM-120D-3 (180) / AAM-4B (120)", A: 95, B: 92, C: 85, D: 94, E: 93, F: 86, LI: 91.2, FPS: 5472},
            {rank: 7, country: "Australia", countryCode: "au", aircraft: "F-35A (44) + F/A-18F (16)", missile: "AIM-120D-3 (180) / AIM-120C-7 (120)", A: 96, B: 94, C: 85, D: 91, E: 91, F: 84, LI: 90.8, FPS: 5448},
            {rank: 8, country: "South Korea", countryCode: "kr", aircraft: "F-35A (40) + KF-21 Block-I (20)", missile: "AIM-120D-3 (180) / AIM-120C-7 (120)", A: 93, B: 90, C: 85, D: 92, E: 91, F: 85, LI: 89.8, FPS: 5388},
            {rank: 9, country: "Italy", countryCode: "it", aircraft: "F-35A/B (28) + Typhoon T4 (32)", missile: "AIM-120D-3 (180) / Meteor (150)", A: 92, B: 90, C: 86, D: 92, E: 90, F: 85, LI: 89.7, FPS: 5382},
            {rank: 10, country: "France", countryCode: "fr", aircraft: "Rafale F4 (36) + F3R (24)", missile: "Meteor (150) / MICA-NG (100)", A: 93, B: 89, C: 84, D: 93, E: 91, F: 86, LI: 89.6, FPS: 5376},
            {rank: 11, country: "Canada", countryCode: "ca", aircraft: "CF-18A/B (60)", missile: "AIM-120C-7 (120)", A: 92, B: 88, C: 85, D: 92, E: 90, F: 88, LI: 89.3, FPS: 5358},
            {rank: 12, country: "Germany", countryCode: "de", aircraft: "Eurofighter T4 (40) + Tornado ECR (20)", missile: "Meteor (150) / AIM-120C-5 (105)", A: 86, B: 78, C: 84, D: 88, E: 86, F: 83, LI: 84.6, FPS: 5076},
            {rank: 13, country: "Pakistan", countryCode: "pk", aircraft: "J-10C (20) + JF-17C (26) + F-16AM-52+ (14)", missile: "PL-15E (200) / AIM-120C-5 (105)", A: 88, B: 75, C: 84, D: 85, E: 78, F: 85, LI: 83.3, FPS: 4998},
            {rank: 14, country: "Spain", countryCode: "es", aircraft: "EF-18M (40) + Eurofighter T4 (20)", missile: "AIM-120C-7 (120) / Meteor (150)", A: 83, B: 76, C: 83, D: 85, E: 83, F: 80, LI: 82.2, FPS: 4932},
            {rank: 15, country: "Saudi Arabia", countryCode: "sa", aircraft: "F-15SA (40) + Typhoon T3 (20)", missile: "AIM-120C-7 (120) / Meteor (150)", A: 82, B: 78, C: 83, D: 79, E: 80, F: 82, LI: 80.8, FPS: 4848},
            {rank: 16, country: "Turkey", countryCode: "tr", aircraft: "F-16C/D Block-70 (35) + F-4E-2020 (25)", missile: "AIM-120C-7 (120)", A: 82, B: 76, C: 81, D: 78, E: 80, F: 82, LI: 79.8, FPS: 4788},
            {rank: 17, country: "Taiwan", countryCode: "tw", aircraft: "F-16V (42) + Mirage-2000-5 (18)", missile: "AIM-120C-7 (120) / MICA-EM (80)", A: 82, B: 74, C: 81, D: 78, E: 80, F: 81, LI: 79.5, FPS: 4770},
            {rank: 18, country: "India", countryCode: "in", aircraft: "Rafale F3R (36) + Su-30MKI Super-30 (24)", missile: "Meteor (150) / RVV-AE-PD (120)", A: 80, B: 80, C: 83, D: 73, E: 80, F: 80, LI: 79.3, FPS: 4758},
            {rank: 19, country: "Greece", countryCode: "gr", aircraft: "F-16V (40) + Mirage-2000-5 Mk2 (20)", missile: "AIM-120C-7 (120) / MICA-EM (80)", A: 81, B: 74, C: 81, D: 77, E: 79, F: 80, LI: 78.9, FPS: 4734},
            {rank: 20, country: "Brazil", countryCode: "br", aircraft: "JAS-39E (20) + F-5EM (40)", missile: "Meteor (150) / AIM-120C-5 (105)", A: 76, B: 74, C: 82, D: 75, E: 78, F: 78, LI: 77.3, FPS: 4638}
        ];

        // Populate rankings table
        const tbody = document.getElementById('rankingsTableBody');
        data.forEach(item => {
            const row = document.createElement('tr');
            row.className = 'table-row border-b border-slate-700/50';
            row.innerHTML = `
                <td class="py-3 text-slate-300">${item.rank}</td>
                <td class="py-3">
                    <img src="https://flagcdn.com/${item.countryCode}.svg" class="flag-img" alt="${item.country}">
                    ${item.country}
                </td>
                <td class="py-3 text-slate-300 text-xs">${item.aircraft}</td>
                <td class="py-3 text-blue-400 text-xs">${item.missile}</td>
                <td class="py-3 text-center font-mono text-yellow-400 font-bold">${item.LI}</td>
                <td class="py-3 text-center font-mono text-green-400">${item.FPS}</td>
                <td class="py-3 text-center font-mono ${item.A >= 95 ? 'text-green-400' : 'text-slate-300'}">${item.A}</td>
                <td class="py-3 text-center font-mono ${item.B >= 90 ? 'text-green-400' : 'text-slate-300'}">${item.B}</td>
                <td class="py-3 text-center font-mono ${item.C >= 90 ? 'text-green-400' : 'text-slate-300'}">${item.C}</td>
                <td class="py-3 text-center font-mono ${item.D >= 95 ? 'text-green-400' : 'text-slate-300'}">${item.D}</td>
                <td class="py-3 text-center font-mono ${item.E >= 90 ? 'text-green-400' : 'text-slate-300'}">${item.E}</td>
                <td class="py-3 text-center font-mono ${item.F >= 85 ? 'text-green-400' : 'text-slate-300'}">${item.F}</td>
            `;
            tbody.appendChild(row);
        });

        // Score distribution
        const scoreDistData = [{
            x: data.map(d => d.country.length > 12 ? d.country.substring(0, 12) + '...' : d.country),
            y: data.map(d => d.LI),
            type: 'bar',
            marker: {
                color: data.map(d => {
                    if (d.LI >= 95) return '#10b981';
                    if (d.LI >= 90) return '#3b82f6';
                    if (d.LI >= 85) return '#f59e0b';
                    return '#ef4444';
                }),
                line: { color: '#1e293b', width: 1 }
            }
        }];
        
        Plotly.newPlot('scoreDistribution', scoreDistData, {
            title: { text: 'Lethality Index by Country', font: { color: '#fff', family: 'Orbitron' } },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: { color: '#94a3b8', tickangle: -45 },
            yaxis: { color: '#94a3b8', title: 'Lethality Index' },
            margin: { t: 50, b: 100, l: 50, r: 20 }
        }, { responsive: true, displayModeBar: false });

        // Radar chart for top 5
        const top5 = data.slice(0, 5);
        const radarData = top5.map(item => ({
            type: 'scatterpolar',
            r: [item.A, item.B, item.C, item.D, item.E, item.F],
            theta: ['Sensor Reach', 'Signature', 'Missile', 'Network', 'ECM', 'Sortie'],
            fill: 'toself',
            name: item.country
        }));
        
        Plotly.newPlot('capabilityRadar', radarData, {
            title: { text: 'Top 5 Multi-Dimensional Analysis', font: { color: '#fff', family: 'Orbitron' } },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            polar: {
                radialaxis: { visible: true, range: [0, 100], color: '#94a3b8' },
                angularaxis: { color: '#94a3b8' }
            },
            showlegend: true,
            legend: { font: { color: '#fff' } },
            margin: { t: 50, b: 20, l: 20, r: 20 }
        }, { responsive: true, displayModeBar: false });

        // Sub-system charts
        const top10 = data.slice(0, 10);
        const chartConfig = { responsive: true, displayModeBar: false };
        const chartLayout = {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            xaxis: { color: '#94a3b8' },
            yaxis: { color: '#94a3b8' },
            margin: { t: 20, b: 80, l: 40, r: 20 }
        };

        function createSubSystemChart(divId, field, color) {
            const chartData = [{
                x: top10.map(d => d.country.length > 10 ? d.country.substring(0, 10) + '...' : d.country),
                y: top10.map(d => d[field]),
                type: 'bar',
                marker: { color: color, line: { color: '#1e293b', width: 1 } }
            }];
            Plotly.newPlot(divId, chartData, {
                ...chartLayout,
                xaxis: { ...chartLayout.xaxis, tickangle: -45 }
            }, chartConfig);
        }

        createSubSystemChart('sensorChart', 'A', '#3b82f6');
        createSubSystemChart('signatureChart', 'B', '#8b5cf6');
        createSubSystemChart('missileChart', 'C', '#ef4444');
        createSubSystemChart('networkChart', 'D', '#10b981');
        createSubSystemChart('ecmChart', 'E', '#f59e0b');
        createSubSystemChart('sortieChart', 'F', '#06b6d4');
