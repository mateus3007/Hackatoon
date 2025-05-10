document.addEventListener('DOMContentLoaded', function() {
  // Gráfico de linguagens mais demandadas
  const languagesCtx = document.getElementById('languagesChart').getContext('2d');
  const languagesChart = new Chart(languagesCtx, {
    type: 'bar',
    data: {
      labels: ['JavaScript', 'Python', 'Java', 'C#', 'PHP', 'Ruby'],
      datasets: [{
        label: 'Demanda Relativa',
        data: [85, 72, 68, 59, 42, 38],
        backgroundColor: [
          'rgba(63, 13, 133, 0.7)',
          'rgba(212, 20, 90, 0.7)',
          'rgba(63, 13, 133, 0.5)',
          'rgba(212, 20, 90, 0.5)',
          'rgba(63, 13, 133, 0.3)',
          'rgba(212, 20, 90, 0.3)'
        ],
        borderColor: [
          'rgba(63, 13, 133, 1)',
          'rgba(212, 20, 90, 1)',
          'rgba(63, 13, 133, 1)',
          'rgba(212, 20, 90, 1)',
          'rgba(63, 13, 133, 1)',
          'rgba(212, 20, 90, 1)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#ccc'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#ccc'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: true
        }
      }
    }
  });

  // Animação das barras de habilidades
  const skillBars = document.querySelectorAll('.skill-level');
  skillBars.forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0';
    setTimeout(() => {
      bar.style.width = width;
    }, 100);
  });
});