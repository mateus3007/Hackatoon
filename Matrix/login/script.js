document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const successMessage = document.getElementById('success-message');
  
  // Verifica se deve mostrar mensagem de sucesso
  if (localStorage.getItem('showSuccessMessage') === 'true') {
    successMessage.textContent = 'Cadastrado com sucesso!';
    successMessage.style.display = 'block';
    localStorage.removeItem('showSuccessMessage');
  }
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const email = form.querySelector('input[type="text"]').value;
    const senha = form.querySelector('input[type="password"]').value;
    
    // Recupera os dados do usuário
    const userData = JSON.parse(localStorage.getItem('userData'));
    
    // Verifica se existe um usuário cadastrado
    if (!userData) {
      alert('Nenhum usuário cadastrado!');
      return;
    }
    
    // Verifica se o email e senha estão corretos
    if (email === userData.email && senha === userData.senha) {
      // Redireciona para a página de perfil
      window.location.href = '../perfil/';
    } else {
      alert('Email ou senha incorretos!');
    }
  });
}); 