// ===================================================================
// SKILLSWAP - ADMIN CHARTS CONTROLLER
// Seamlessly adapts to Light and Dark Theme toggles
// ===================================================================

document.addEventListener('DOMContentLoaded', async () => {
  const catCanvas = document.getElementById('categoryChart');
  const statusCanvas = document.getElementById('statusChart');

  if (!catCanvas || !statusCanvas) return;

  try {
    const res = await fetch('/admin/api/chart-data');
    if (!res.ok) return;
    const chartData = await res.json();

    function getThemeColors() {
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      return {
        textColor: isDark ? '#C3C9D4' : '#50596A',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(11, 19, 43, 0.08)',
        doughnutBorder: isDark ? '#1C2541' : '#FFFFFF'
      };
    }

    let colors = getThemeColors();

    // 1. Category Bar Chart: Offered vs Wanted
    const categoryChart = new Chart(catCanvas, {
      type: 'bar',
      data: {
        labels: chartData.categories.labels,
        datasets: [
          {
            label: 'Skills Offered (Teaching)',
            data: chartData.categories.offered,
            backgroundColor: 'rgba(212, 175, 119, 0.85)',
            borderColor: '#D4AF77',
            borderWidth: 1,
            borderRadius: 4
          },
          {
            label: 'Skills Wanted (Learning)',
            data: chartData.categories.wanted,
            backgroundColor: 'rgba(28, 37, 65, 0.85)',
            borderColor: '#1C2541',
            borderWidth: 1,
            borderRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            labels: { color: colors.textColor, font: { family: 'Plus Jakarta Sans, sans-serif', weight: 600 } }
          }
        },
        scales: {
          x: {
            ticks: { color: colors.textColor, font: { size: 11 } },
            grid: { color: colors.gridColor }
          },
          y: {
            ticks: { color: colors.textColor, stepSize: 1 },
            grid: { color: colors.gridColor }
          }
        }
      }
    });

    // 2. Swap Status Doughnut Chart
    const statusChart = new Chart(statusCanvas, {
      type: 'doughnut',
      data: {
        labels: chartData.swap_status.labels,
        datasets: [{
          data: chartData.swap_status.data,
          backgroundColor: [
            '#D4AF77', // Pending (champagne gold)
            '#3B82F6', // Active (blue)
            '#10B981', // Completed (emerald)
            '#EF4444'  // Rejected/Cancelled (rose)
          ],
          borderColor: colors.doughnutBorder,
          borderWidth: 3
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: colors.textColor, padding: 15, font: { family: 'Plus Jakarta Sans, sans-serif', weight: 600 } }
          }
        },
        cutout: '68%'
      }
    });

    // Re-theme charts whenever user toggles light/dark mode
    window.addEventListener('skillswap:themechange', () => {
      colors = getThemeColors();
      
      categoryChart.options.plugins.legend.labels.color = colors.textColor;
      categoryChart.options.scales.x.ticks.color = colors.textColor;
      categoryChart.options.scales.x.grid.color = colors.gridColor;
      categoryChart.options.scales.y.ticks.color = colors.textColor;
      categoryChart.options.scales.y.grid.color = colors.gridColor;
      categoryChart.update();

      statusChart.data.datasets[0].borderColor = colors.doughnutBorder;
      statusChart.options.plugins.legend.labels.color = colors.textColor;
      statusChart.update();
    });

  } catch (err) {
    console.error('Failed to load chart data:', err);
  }
});
