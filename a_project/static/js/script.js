const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
const icons = document.querySelectorAll('.form-group i');

inputs.forEach((input, index) => {
  input.addEventListener('focus', () => {
    icons[index].style.color = '#000';
  });

  input.addEventListener('blur', () => {
    icons[index].style.color = 'rgb(212, 212, 212)';
  });
});