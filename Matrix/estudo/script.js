document.addEventListener('DOMContentLoaded', function() {
  const progressBar = document.querySelector('.progress-bar');
  setTimeout(() => {
    progressBar.style.width = '35%';
  }, 500);

  const skills = document.querySelectorAll('.step-skills li');
  skills.forEach(skill => {
    skill.addEventListener('click', function() {
      const icon = this.querySelector('i');
      if (icon.classList.contains('fa-circle')) {
        icon.classList.remove('fa-circle');
        icon.classList.add('fa-check-circle');
        icon.style.color = '#4CAF50';
      } else {
        icon.classList.remove('fa-check-circle');
        icon.classList.add('fa-circle');
        icon.style.color = '';
      }
    });
  });

  const steps = document.querySelectorAll('.step');
  steps.forEach(step => {
    step.addEventListener('click', function() {
      steps.forEach(s => s.classList.remove('active'));
      this.classList.add('active');
    });
  });
});
