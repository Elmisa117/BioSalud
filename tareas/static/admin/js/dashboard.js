function randomColors(count) {
    const baseColors = ['#0d6efd','#20c997','#6610f2','#ffc107','#dc3545','#198754','#6c757d'];
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(baseColors[i % baseColors.length]);
    }
    return colors;
}

document.addEventListener('DOMContentLoaded', function () {
    if (typeof pagosMetodo !== 'undefined') {
        const ctx = document.getElementById('metodoPagoChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: Object.keys(pagosMetodo),
                    datasets: [{
                        data: Object.values(pagosMetodo),
                        backgroundColor: randomColors(Object.keys(pagosMetodo).length)
                    }]
                },
                options: {plugins: {legend: {position: 'bottom'}}}
            });
        }
    }

    const camaCtx = document.getElementById('camasChart');
    if (camaCtx) {
        new Chart(camaCtx, {
            type: 'doughnut',
            data: {
                labels: ['Ocupadas', 'Disponibles'],
                datasets: [{
                    data: [camasOcupadas, camasDisponibles],
                    backgroundColor: ['#20c997', '#6c757d']
                }]
            },
            options: {plugins: {legend: {position: 'bottom'}}}
        });
    }

    const diagCtx = document.getElementById('diagChart');
    if (diagCtx) {
        new Chart(diagCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(diagnosticosData),
                datasets: [{
                    label: 'Diagnósticos',
                    data: Object.values(diagnosticosData),
                    backgroundColor: randomColors(Object.keys(diagnosticosData).length)
                }]
            },
            options: {plugins: {legend: {display: false}}}
        });
    }

    const actCtx = document.getElementById('actividadChart');
    if (actCtx) {
        const labels = Object.keys(actividadData).sort((a, b) => parseInt(a) - parseInt(b));
        const data = labels.map(h => actividadData[h]);
        new Chart(actCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Actividad',
                    data: data,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13,110,253,0.2)',
                    tension: 0.3
                }]
            },
            options: {scales: {y: {beginAtZero: true}}}
        });
    }

    const rolCtx = document.getElementById('rolChart');
    if (rolCtx) {
        const labels = Object.keys(accionesData);
        const data = labels.map(r => accionesData[r]);
        new Chart(rolCtx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Acciones',
                    data: data,
                    backgroundColor: randomColors(labels.length)
                }]
            },
            options: {plugins: {legend: {display: false}}, scales: {y: {beginAtZero: true}}}
        });
    }
});
