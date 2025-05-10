// Profile data structure
let profileData = {
  fullName: '',
  email: '',
  phone: '',
  area: '',
  skills: [],
  experience: '',
  profilePicture: null
};

// Load profile data from localStorage
function loadProfileData() {
  const savedData = localStorage.getItem('profileData');
  if (savedData) {
    profileData = JSON.parse(savedData);
    updateProfileView();
    document.getElementById('formContainer').style.display = 'none';
    document.getElementById('profileView').style.display = 'block';
  }
}

// Save profile data to localStorage
function saveProfileData() {
  localStorage.setItem('profileData', JSON.stringify(profileData));
}

// Update profile view with current data
function updateProfileView() {
  document.getElementById('viewFullName').textContent = profileData.fullName;
  document.getElementById('viewEmail').textContent = profileData.email;
  document.getElementById('viewPhone').textContent = profileData.phone;
  document.getElementById('viewArea').textContent = profileData.area;
  document.getElementById('viewExperience').textContent = profileData.experience;

  // Update skills view
  const skillsView = document.getElementById('viewSkills');
  skillsView.innerHTML = '';
  profileData.skills.forEach(skill => {
    const skillTag = document.createElement('span');
    skillTag.className = 'skill-tag';
    skillTag.textContent = skill;
    skillsView.appendChild(skillTag);
  });

  // Update profile picture
  if (profileData.profilePicture) {
    const profilePictureView = document.getElementById('profilePictureView');
    profilePictureView.innerHTML = `<img src="${profileData.profilePicture}" alt="Profile Picture">`;
  }
}

// Handle profile picture upload
document.getElementById('changePicture').addEventListener('click', () => {
  document.getElementById('profilePicture').click();
});

document.getElementById('profilePicture').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      profileData.profilePicture = e.target.result;
      const profilePictureView = document.getElementById('profilePictureView');
      profilePictureView.innerHTML = `<img src="${e.target.result}" alt="Profile Picture">`;
    };
    reader.readAsDataURL(file);
  }
});

// Handle form submission
document.getElementById('profileForm').addEventListener('submit', (e) => {
  e.preventDefault();
  
  // Get current skills from the container
  const currentSkills = Array.from(document.querySelectorAll('#skillsContainer .skill-tag'))
    .map(tag => tag.textContent.replace(' ×', ''));

  profileData = {
    fullName: document.getElementById('fullName').value,
    email: document.getElementById('email').value,
    phone: document.getElementById('phone').value,
    area: document.getElementById('area').value,
    skills: currentSkills,
    experience: document.getElementById('experience').value,
    profilePicture: profileData.profilePicture
  };

  saveProfileData();
  updateProfileView();
  
  document.getElementById('formContainer').style.display = 'none';
  document.getElementById('profileView').style.display = 'block';
});

// Handle edit profile button
document.getElementById('editProfile').addEventListener('click', () => {
  document.getElementById('profileView').style.display = 'none';
  document.getElementById('formContainer').style.display = 'block';
  
  // Fill form with current data
  document.getElementById('fullName').value = profileData.fullName;
  document.getElementById('email').value = profileData.email;
  document.getElementById('phone').value = profileData.phone;
  document.getElementById('area').value = profileData.area;
  document.getElementById('experience').value = profileData.experience;
  
  // Fill skills
  const skillsContainer = document.getElementById('skillsContainer');
  skillsContainer.innerHTML = '';
  profileData.skills.forEach(skill => {
    addSkillTag(skill);
  });
});

// Function to add a skill tag
function addSkillTag(skillText) {
  const skillsContainer = document.getElementById('skillsContainer');
  const skillTag = document.createElement('div');
  skillTag.className = 'skill-tag';
  skillTag.textContent = skillText;
  
  const removeBtn = document.createElement('span');
  removeBtn.textContent = ' ×';
  removeBtn.style.cursor = 'pointer';
  removeBtn.style.marginLeft = '5px';
  removeBtn.addEventListener('click', () => {
    skillsContainer.removeChild(skillTag);
    // Update profileData when removing a skill
    profileData.skills = Array.from(document.querySelectorAll('#skillsContainer .skill-tag'))
      .map(tag => tag.textContent.replace(' ×', ''));
    saveProfileData();
  });
  
  skillTag.appendChild(removeBtn);
  skillsContainer.appendChild(skillTag);
}

// Handle adding skills
document.getElementById('addSkill').addEventListener('click', () => {
  const skillInput = document.getElementById('skillInput');
  
  if (skillInput.value.trim() !== '') {
    addSkillTag(skillInput.value.trim());
    // Update profileData when adding a skill
    profileData.skills = Array.from(document.querySelectorAll('#skillsContainer .skill-tag'))
      .map(tag => tag.textContent.replace(' ×', ''));
    saveProfileData();
    skillInput.value = '';
  }
});

// Load profile data when page loads
document.addEventListener('DOMContentLoaded', loadProfileData);