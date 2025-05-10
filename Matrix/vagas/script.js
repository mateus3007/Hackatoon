// Job data structure - can be replaced with API data later
const jobsData = [
  {
    id: 1,
    title: "Desenvolvedor Front-end Júnior",
    company: "Tech Solutions",
    location: "São Paulo/SP",
    description: "Buscamos desenvolvedor com conhecimento em HTML, CSS e JavaScript para integrar nosso time.",
    skills: ["HTML", "CSS", "JavaScript", "React"],
    type: "Front-end",
    level: "Júnior"
  },
  {
    id: 2,
    title: "UI Designer",
    company: "Creative Agency",
    location: "Remoto",
    description: "Vaga para designer com foco em interfaces web e mobile.",
    skills: ["Figma", "UI Design", "Prototipação", "Adobe XD"],
    type: "Design",
    level: "Pleno"
  },
  {
    id: 3,
    title: "Desenvolvedor Back-end Pleno",
    company: "Data Systems",
    location: "Rio de Janeiro/RJ",
    description: "Desenvolvimento de APIs RESTful e microsserviços.",
    skills: ["Java", "Spring Boot", "MongoDB", "AWS"],
    type: "Back-end",
    level: "Pleno"
  },
  {
    id: 4,
    title: "Full Stack Developer",
    company: "Innovation Labs",
    location: "Remoto",
    description: "Desenvolvimento full stack com foco em aplicações web modernas.",
    skills: ["React", "Node.js", "PostgreSQL", "Docker"],
    type: "Full-stack",
    level: "Sênior"
  },
  {
    id: 5,
    title: "DevOps Engineer",
    company: "Cloud Solutions",
    location: "São Paulo/SP",
    description: "Gerenciamento de infraestrutura cloud e automação de processos.",
    skills: ["AWS", "Docker", "Kubernetes", "Terraform"],
    type: "DevOps",
    level: "Pleno"
  }
];

// Get user profile data
function getUserProfile() {
  const profileData = localStorage.getItem('profileData');
  return profileData ? JSON.parse(profileData) : null;
}

// Calculate compatibility percentage based on skills
function calculateCompatibility(jobSkills, userSkills) {
  if (!userSkills || userSkills.length === 0) return 0;
  
  const matchingSkills = jobSkills.filter(skill => 
    userSkills.some(userSkill => 
      userSkill.toLowerCase() === skill.toLowerCase()
    )
  );
  
  return Math.round((matchingSkills.length / jobSkills.length) * 100);
}

// Function to render jobs
function renderJobs(jobs) {
  const jobsList = document.querySelector('.jobs-list');
  jobsList.innerHTML = ''; // Clear existing jobs
  const userProfile = getUserProfile();
  const userSkills = userProfile ? userProfile.skills : [];

  jobs.forEach(job => {
    // Calculate compatibility percentage
    const compatibilityPercentage = calculateCompatibility(job.skills, userSkills);
    
    const jobCard = document.createElement('div');
    jobCard.className = 'job-card';
    jobCard.innerHTML = `
      <div class="job-compatibility-badge ${compatibilityPercentage >= 70 ? 'high-compatibility' : compatibilityPercentage >= 40 ? 'medium-compatibility' : 'low-compatibility'}">${compatibilityPercentage}% Compatível</div>
      <h2>${job.title}</h2>
      <p class="company">${job.company} • ${job.location}</p>
      <p class="description">${job.description}</p>
      <div class="skills">
        ${job.skills.map(skill => {
          const hasSkill = userSkills.some(userSkill => 
            userSkill.toLowerCase() === skill.toLowerCase()
          );
          return `<span class="skill-tag">
            <i class="fas ${hasSkill ? 'fa-check' : 'fa-times'}"></i>
            ${skill}
          </span>`;
        }).join('')}
      </div>
      <a href="#" class="btn-apply" data-job-id="${job.id}">Candidatar-se</a>
    `;
    jobsList.appendChild(jobCard);
  });
}

// Filter functions
function filterJobs() {
  const areaFilter = document.querySelector('select:nth-child(1)').value;
  const levelFilter = document.querySelector('select:nth-child(2)').value;

  let filteredJobs = [...jobsData];

  if (areaFilter !== 'Filtrar por área') {
    filteredJobs = filteredJobs.filter(job => job.type === areaFilter);
  }

  if (levelFilter !== 'Filtrar por nível') {
    filteredJobs = filteredJobs.filter(job => job.level === levelFilter);
  }

  renderJobs(filteredJobs);
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
  // Initial render
  renderJobs(jobsData);

  // Add filter listeners
  document.querySelectorAll('.filters select').forEach(select => {
    select.addEventListener('change', filterJobs);
  });

  // Add click listeners for apply buttons
  document.querySelector('.jobs-list').addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-apply')) {
      const jobId = e.target.dataset.jobId;
      // Here you can add the application logic or redirect to application page
      console.log(`Applying for job ${jobId}`);
    }
  });
});

// Function to update jobs from AI API (to be implemented)
async function updateJobsFromAI() {
  try {
    // This is where you'll integrate with your AI API
    // const response = await fetch('your-ai-api-endpoint');
    // const aiJobs = await response.json();
    // renderJobs(aiJobs);
  } catch (error) {
    console.error('Error fetching AI recommendations:', error);
  }
}

// Função para adicionar habilidades no perfil
document.getElementById('addSkill')?.addEventListener('click', function() {
  const skillInput = document.getElementById('skillInput');
  const skillsContainer = document.getElementById('skillsContainer');
  
  if (skillInput.value.trim() !== '') {
    const skillTag = document.createElement('div');
    skillTag.className = 'skill-tag';
    skillTag.textContent = skillInput.value.trim();
    
    const removeBtn = document.createElement('span');
    removeBtn.textContent = ' ×';
    removeBtn.style.cursor = 'pointer';
    removeBtn.style.marginLeft = '5px';
    removeBtn.addEventListener('click', function() {
      skillsContainer.removeChild(skillTag);
    });
    
    skillTag.appendChild(removeBtn);
    skillsContainer.appendChild(skillTag);
    skillInput.value = '';
  }
});

// Simulação de login
document.getElementById('loginForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  // Simular login bem-sucedido
  window.location.href = 'vagas.html';
});

// Simulação de salvamento de perfil
document.getElementById('profileForm')?.addEventListener('submit', function(e) {
  e.preventDefault();
  alert('Perfil salvo com sucesso!');
  window.location.href = 'vagas.html';
});