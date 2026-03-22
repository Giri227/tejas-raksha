// Tejas Raksha Security Scanner - Report Scripts

// Chart.js CDN (embedded inline for no external dependencies)
// Simplified chart implementation

document.addEventListener('DOMContentLoaded', function() {
    // Initialize severity chart
    initSeverityChart();
    
    // Initialize filter controls
    initFilterControls();
});

function downloadReport() {
    // Get the current HTML content
    const htmlContent = document.documentElement.outerHTML;
    
    // Create a Blob with the HTML content
    const blob = new Blob([htmlContent], { type: 'text/html' });
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    // Generate filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    a.download = `tejas_raksha_report_${timestamp}.html`;
    
    // Trigger download
    document.body.appendChild(a);
    a.click();
    
    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function initSeverityChart() {
    const canvas = document.getElementById('severityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Get severity counts from the page
    const severityBoxes = document.querySelectorAll('.severity-box');
    const data = {
        labels: [],
        values: [],
        colors: []
    };
    
    severityBoxes.forEach(box => {
        const label = box.querySelector('.label').textContent;
        const count = parseInt(box.querySelector('.count').textContent);
        
        data.labels.push(label);
        data.values.push(count);
        
        // Get color from box class
        if (box.classList.contains('high')) {
            data.colors.push('#e74c3c');
        } else if (box.classList.contains('medium')) {
            data.colors.push('#f39c12');
        } else if (box.classList.contains('low')) {
            data.colors.push('#3498db');
        } else {
            data.colors.push('#95a5a6');
        }
    });
    
    // Draw simple bar chart
    drawBarChart(ctx, data);
}

function drawBarChart(ctx, data) {
    const canvas = ctx.canvas;
    const width = canvas.width = canvas.offsetWidth;
    const height = canvas.height = 300;
    
    const padding = 40;
    const barWidth = (width - padding * 2) / data.values.length;
    const maxValue = Math.max(...data.values, 1);
    const scale = (height - padding * 2) / maxValue;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw bars
    data.values.forEach((value, index) => {
        const barHeight = value * scale;
        const x = padding + index * barWidth + barWidth * 0.1;
        const y = height - padding - barHeight;
        const w = barWidth * 0.8;
        
        // Draw bar
        ctx.fillStyle = data.colors[index];
        ctx.fillRect(x, y, w, barHeight);
        
        // Draw value on top
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(value, x + w / 2, y - 5);
        
        // Draw label
        ctx.fillStyle = '#666';
        ctx.font = '14px sans-serif';
        ctx.fillText(data.labels[index], x + w / 2, height - padding + 20);
    });
    
    // Draw title
    ctx.fillStyle = '#2c3e50';
    ctx.font = 'bold 18px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Findings by Severity', width / 2, 25);
}

function initFilterControls() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const findingRows = document.querySelectorAll('.finding-row');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const severity = this.getAttribute('data-severity');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter rows
            findingRows.forEach(row => {
                if (severity === 'all' || row.getAttribute('data-severity') === severity) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Table sorting functionality
function sortTable(columnIndex) {
    const table = document.getElementById('findingsTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        return aText.localeCompare(bText);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
