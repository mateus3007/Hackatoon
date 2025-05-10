document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const nome = form.querySelector('input[type="text"]').value;
    const email = form.querySelector('input[type="email"]').value;
    const senha = form.querySelector('input[type="password"]').value;
    const confirmarSenha = form.querySelectorAll('input[type="password"]')[1].value;
    
    // Verifica se as senhas são iguais
    if (senha !== confirmarSenha) {
      alert('As senhas não coincidem!');
      return;
    }
    
    // Armazena os dados do usuário
    const userData = {
      nome,
      email,
      senha
    };
    
    localStorage.setItem('userData', JSON.stringify(userData));
    localStorage.setItem('showSuccessMessage', 'true');
    
    // Redireciona para a página de login
    window.location.href = '/login/';
  });
}); 