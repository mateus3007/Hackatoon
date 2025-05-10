document.addEventListener('DOMContentLoaded', function() {
  const areaSelect = document.getElementById('areaSelect');
  const careerAreaSpan = document.getElementById('careerArea');
  const trendsContent = document.getElementById('trendsContent');
  const trendsTemplate = document.getElementById('trendsTemplate');
  
  // Dados das tendências por área
  const trendsData = {
    'data-science': {
      market: [
        "Crescimento de 27% na demanda por cientistas de dados em 2023",
        "Setores financeiro e saúde são os que mais contratam",
        "Python e SQL continuam sendo requisitos essenciais",
        "Grande demanda por profissionais com experiência em Big Data"
      ],
      future: [
        "Aumento na demanda por especialistas em LLMs e GPT",
        "Ênfase em ética e governança de dados",
        "Integração entre ciência de dados e engenharia de dados",
        "Crescimento de aplicações de IA generativa"
      ],
      salaries: [
        { level: "Júnior", range: "R$ 4.500 - R$ 7.000" },
        { level: "Pleno", range: "R$ 7.500 - R$ 12.000" },
        { level: "Sênior", range: "R$ 13.000+" },
        { level: "Especialista", range: "R$ 18.000+" }
      ],
      skills: [
        "Machine Learning Explainability",
        "MLOps",
        "Processamento de Linguagem Natural",
        "Data Storytelling",
        "Engenharia de Features",
        "Cloud Computing (AWS/GCP/Azure)"
      ]
    },
    'web-dev': {
      market: [
        "React continua dominando o mercado front-end",
        "Aumento de 40% em vagas para Full Stack em 2023",
        "Typescript se tornou requisito em 65% das vagas",
        "Demanda crescente por desenvolvedores com conhecimento em acessibilidade"
      ],
      future: [
        "WebAssembly ganhando espaço para aplicações pesadas",
        "Aplicações progressivas (PWA) substituindo apps nativos",
        "Low-code para prototipagem rápida",
        "Maior integração entre front-end e inteligência artificial"
      ],
      salaries: [
        { level: "Júnior", range: "R$ 3.500 - R$ 5.500" },
        { level: "Pleno", range: "R$ 6.000 - R$ 9.000" },
        { level: "Sênior", range: "R$ 10.000+" },
        { level: "Arquiteto", range: "R$ 15.000+" }
      ],
      skills: [
        "Micro frontends",
        "Server Components",
        "Web3 e Blockchains",
        "Acessibilidade Web",
        "GraphQL",
        "Testes automatizados (Jest, Cypress)"
      ]
    },
    'mobile': {
      market: [
        "React Native lidera em aplicações multiplataforma",
        "Kotlin é preferido para Android nativo",
        "SwiftUI ganha adoção rápida no ecossistema iOS",
        "Demanda por apps com integração IoT cresce 35%"
      ],
      future: [
        "Maior integração entre mobile e wearables",
        "Aplicações com realidade aumentada",
        "Otimização para dispositivos foldables",
        "Adoção de Kotlin Multiplatform"
      ],
      salaries: [
        { level: "Júnior", range: "R$ 4.000 - R$ 6.000" },
        { level: "Pleno", range: "R$ 6.500 - R$ 9.500" },
        { level: "Sênior", range: "R$ 11.000+" },
        { level: "Especialista", range: "R$ 16.000+" }
      ],
      skills: [
        "Jetpack Compose",
        "SwiftUI",
        "Flutter",
        "Testes em dispositivos reais",
        "Performance mobile",
        "Segurança em aplicativos"
      ]
    },
    'devops': {
      market: [
        "Demanda por profissionais DevOps cresceu 50% em 2023",
        "AWS lidera, mas Azure e GCP ganham mercado",
        "Kubernetes se tornou requisito básico",
        "Segurança em cloud é a habilidade mais valorizada"
      ],
      future: [
        "GitOps como padrão para entrega contínua",
        "Infraestrutura como código se torna obrigatória",
        "Maior automação com AIOps",
        "Crescimento de serverless e edge computing"
      ],
      salaries: [
        { level: "Júnior", range: "R$ 5.000 - R$ 7.500" },
        { level: "Pleno", range: "R$ 8.000 - R$ 12.000" },
        { level: "Sênior", range: "R$ 14.000+" },
        { level: "Arquiteto", range: "R$ 20.000+" }
      ],
      skills: [
        "Terraform",
        "ArgoCD",
        "Service Mesh (Istio/Linkerd)",
        "Observabilidade (OpenTelemetry)",
        "FinOps",
        "Security as Code"
      ]
    },
    'ux-ui': {
      market: [
        "Design Systems são requisito em 80% das vagas",
        "Figma domina o mercado de ferramentas",
        "Crescimento de vagas para UX Research",
        "Designers com noção de front-end são mais valorizados"
      ],
      future: [
        "Design para interfaces de voz e gestos",
        "Aumento de designs para realidade aumentada",
        "Adaptação para diversos dispositivos (IoT, wearables)",
        "Maior integração entre design e inteligência artificial"
      ],
      salaries: [
        { level: "Júnior", range: "R$ 3.500 - R$ 5.000" },
        { level: "Pleno", range: "R$ 5.500 - R$ 8.500" },
        { level: "Sênior", range: "R$ 9.000+" },
        { level: "Líder", range: "R$ 13.000+" }
      ],
      skills: [
        "Design de Microinterações",
        "UX Writing",
        "Prototipagem avançada",
        "Acessibilidade digital",
        "Pesquisa com usuários",
        "Motion Design"
      ]
    }
  };

  areaSelect.addEventListener('change', function() {
    const selectedArea = this.value;
    
    if (!selectedArea) {
      showEmptyState();
      return;
    }
    
    const areaName = this.options[this.selectedIndex].text;
    careerAreaSpan.textContent = areaName;
    
    loadTrendsData(selectedArea);
  });

  function showEmptyState() {
    trendsContent.innerHTML = `
      <div class="empty-state">
        <i class="fas fa-chart-line"></i>
        <p>Selecione uma área para visualizar as tendências</p>
      </div>
    `;
    careerAreaSpan.textContent = "Sua Área";
  }

  function loadTrendsData(area) {
    const data = trendsData[area];
    if (!data) return;
    
    // Clona o template
    const content = trendsTemplate.content.cloneNode(true);
    trendsContent.innerHTML = '';
    trendsContent.appendChild(content);
    
    // Preenche os dados
    fillTrendList('marketTrends', data.market);
    fillTrendList('futureTrends', data.future);
    fillSalaryData('salaryTrends', data.salaries);
    fillSkillsData('skillsTrends', data.skills);
  }

  function fillTrendList(elementId, items) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = '';
    const ul = document.createElement('ul');
    
    items.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      ul.appendChild(li);
    });
    
    element.appendChild(ul);
  }

  function fillSalaryData(elementId, salaries) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = '';
    const div = document.createElement('div');
    div.className = 'salary-levels';
    
    salaries.forEach(salary => {
      const salaryDiv = document.createElement('div');
      salaryDiv.className = 'salary-level';
      salaryDiv.innerHTML = `
        <span>${salary.level}</span>
        <span>${salary.range}</span>
      `;
      div.appendChild(salaryDiv);
    });
    
    element.appendChild(div);
  }

  function fillSkillsData(elementId, skills) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = '';
    skills.forEach(skill => {
      const span = document.createElement('span');
      span.className = 'skill-tag';
      span.textContent = skill;
      element.appendChild(span);
    });
  }
});